import sys
import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import unittest
from datetime import date
from unittest.mock import patch

from dedupe import is_duplicate
import pipeline
import blogger
import images
import integration_check
from rss_collector import _image_url


class PipelineTests(unittest.TestCase):
    def test_cloudinary_missing_settings_reports_names_only(self):
        with patch.dict("os.environ", {}, clear=True):
            missing = images.missing_cloudinary_settings()

        self.assertEqual(missing, list(images.CLOUDINARY_SETTINGS))

    def test_cloudinary_source_validation_rejects_untrusted_urls(self):
        self.assertTrue(images.is_approved_news_image_url("https://cdn.abplive.com/image.jpg"))
        self.assertFalse(images.is_approved_news_image_url("http://cdn.abplive.com/image.jpg"))
        self.assertFalse(images.is_approved_news_image_url("https://attacker.example/image.jpg"))

    def test_rss_image_extraction_only_returns_approved_https_sources(self):
        item = ElementTree.fromstring(
            '<item><description><![CDATA[<img src="https://cdn.abplive.com/news.jpg">]]></description></item>'
        )
        self.assertEqual(
            _image_url(item, item.findtext("description")),
            "https://cdn.abplive.com/news.jpg",
        )

    def test_cloudinary_smoke_check_removes_temporary_asset(self):
        uploader = unittest.mock.Mock()
        uploader.upload.return_value = {
            "public_id": "padma-bangla-news/integration-tests/test-asset",
            "secure_url": "https://res.cloudinary.com/demo/test.png",
        }
        uploader.destroy.return_value = {"result": "ok"}
        settings = {
            "CLOUDINARY_CLOUD_NAME": "demo",
            "CLOUDINARY_API_KEY": "test-key",
            "CLOUDINARY_API_SECRET": "test-secret",
        }
        with tempfile.TemporaryDirectory() as directory:
            fallback = Path(directory) / "branded-test.png"
            fallback.write_bytes(b"test image")
            with (
                patch.dict("os.environ", settings, clear=True),
                patch.object(images, "_cloudinary_client", return_value=(uploader, unittest.mock.Mock())),
                patch.object(images, "_branded_fallback_path", return_value=fallback),
            ):
                result = images.verify_cloudinary_upload_and_cleanup()

            self.assertEqual(result["uploaded_and_removed"], True)
            self.assertFalse(fallback.exists())
        uploader.destroy.assert_called_once_with(
            "padma-bangla-news/integration-tests/test-asset",
            invalidate=True,
            resource_type="image",
        )

    def test_branded_fallback_is_a_valid_bitmap(self):
        from PIL import Image

        fallback = images._branded_fallback_path()
        try:
            with Image.open(fallback) as image:
                self.assertEqual(image.size, (1200, 675))
                self.assertEqual(image.format, "PNG")
        finally:
            fallback.unlink(missing_ok=True)

    def test_cloudinary_upload_returns_transformed_secure_url(self):
        uploader = unittest.mock.Mock()
        uploader.upload.return_value = {"public_id": "padma-bangla-news/news/news-abc"}
        utils = unittest.mock.Mock()
        utils.cloudinary_url.return_value = (
            "https://res.cloudinary.com/padma/image/upload/c_limit/news-abc.jpg",
            {},
        )
        environment = {
            "CLOUDINARY_CLOUD_NAME": "test-cloud",
            "CLOUDINARY_API_KEY": "test-key",
            "CLOUDINARY_API_SECRET": "test-secret",
        }
        with (
            patch.dict("os.environ", environment, clear=True),
            patch.object(images, "_cloudinary_client", return_value=(uploader, utils)),
        ):
            url = images.upload_news_image("https://cdn.abplive.com/image.jpg", "abc")

        self.assertTrue(url.startswith("https://res.cloudinary.com/"))
        uploader.upload.assert_called_once()

    def test_installed_cloudinary_sdk_generates_secure_delivery_url(self):
        import cloudinary

        cloudinary.config(
            cloud_name="test-cloud",
            api_key="test-key",
            api_secret="test-secret",
            secure=True,
        )
        url = images._cloudinary_url(cloudinary.utils, "padma-bangla-news/news/test")

        self.assertTrue(url.startswith("https://res.cloudinary.com/test-cloud/image/upload/"))

    def test_cloudinary_image_is_added_as_a_safe_article_figure(self):
        result = pipeline._article_content_with_image(
            {"headline": 'শিরোনাম "বিশেষ"', "article_html": "<p>সংবাদ</p>"},
            "https://res.cloudinary.com/demo/image/upload/news.jpg",
        )

        self.assertIn("<figure><img", result)
        self.assertIn("alt=\"শিরোনাম &quot;বিশেষ&quot;\"", result)
        self.assertTrue(result.endswith("<p>সংবাদ</p>"))

    def test_facebook_page_check_is_read_only_and_keeps_token_out_of_url(self):
        environment = {"FACEBOOK_PAGE_ID": "123", "FACEBOOK_PAGE_ACCESS_TOKEN": "not-logged"}
        with (
            patch.dict("os.environ", environment, clear=True),
            patch.object(
                pipeline,
                "_request_json",
                return_value={"id": "123", "name": "Padma Bangla News"},
            ) as request,
        ):
            result = pipeline.verify_facebook_page()

        self.assertEqual(result["status"], "success")
        args, kwargs = request.call_args
        self.assertNotIn("not-logged", args[0])
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer not-logged")

    def test_cloudinary_failure_blocks_blogger_and_facebook(self):
        item = {
            "source_id": "source-image-failure",
            "status": "ready",
            "priority_score": 300,
            "article": {"headline": "শিরোনাম", "article_html": "<p>খবর</p>"},
        }
        environment = {
            "NEWS_PUBLISHING_ENABLED": "true",
            "GITHUB_EVENT_NAME": "schedule",
            "BLOGGER_BLOG_ID": "blog",
            "BLOGGER_CLIENT_ID": "client",
            "BLOGGER_CLIENT_SECRET": "secret",
            "BLOGGER_REFRESH_TOKEN": "refresh",
        }
        with (
            patch.dict("os.environ", environment, clear=True),
            patch.object(pipeline, "load_queue", return_value=[item]),
            patch.object(pipeline, "_collect_stories", return_value=[]),
            patch.object(pipeline, "save_queue"),
            patch.object(pipeline, "count_published_today", return_value=0),
            patch.object(pipeline, "upload_news_image", side_effect=images.ImageIntegrationError("Cloudinary unavailable")),
            patch.object(pipeline, "publish_post") as publish_blog,
            patch.object(pipeline, "publish_facebook") as publish_page,
        ):
            pipeline.run_pipeline()

        publish_blog.assert_not_called()
        publish_page.assert_not_called()
        self.assertEqual(item["status"], "ready")

    def test_integration_check_never_prints_exception_text(self):
        secret_sentinel = "credential-value-must-not-be-logged"
        environment = {name: secret_sentinel for name in integration_check.REQUIRED_SETTINGS}
        output = io.StringIO()
        with (
            patch.dict("os.environ", environment, clear=True),
            patch.object(blogger, "test_connection", side_effect=RuntimeError(secret_sentinel)),
            patch.object(pipeline, "verify_facebook_page", return_value={"status": "success"}),
            patch.object(images, "verify_cloudinary_upload_and_cleanup", return_value={"status": "success"}),
            redirect_stdout(output),
        ):
            exit_code = integration_check.main()

        self.assertEqual(exit_code, 1)
        self.assertNotIn(secret_sentinel, output.getvalue())
        self.assertIn("Blogger OAuth: failed (RuntimeError)", output.getvalue())

    def test_integration_check_preflight_lists_names_without_network_calls(self):
        output = io.StringIO()
        with (
            patch.dict("os.environ", {}, clear=True),
            patch.object(blogger, "test_connection") as blogger_check,
            patch.object(pipeline, "verify_facebook_page") as facebook_check,
            patch.object(images, "verify_cloudinary_upload_and_cleanup") as cloudinary_check,
            redirect_stdout(output),
        ):
            exit_code = integration_check.main()

        self.assertEqual(exit_code, 1)
        self.assertIn("BLOGGER_REFRESH_TOKEN", output.getvalue())
        self.assertIn("FACEBOOK_PAGE_ACCESS_TOKEN", output.getvalue())
        self.assertIn("CLOUDINARY_API_SECRET", output.getvalue())
        blogger_check.assert_not_called()
        facebook_check.assert_not_called()
        cloudinary_check.assert_not_called()

    def test_blogger_connection_test_creates_draft_only(self):
        service = unittest.mock.Mock()
        service.blogs.return_value.get.return_value.execute.return_value = {"name": "Padma Blog"}
        service.posts.return_value.insert.return_value.execute.return_value = {
            "id": "draft-1",
            "status": "DRAFT",
        }

        with (
            patch.dict("os.environ", {"BLOGGER_BLOG_ID": "blog-id"}, clear=True),
            patch.object(blogger, "get_service", return_value=service),
        ):
            result = blogger.test_connection()

        self.assertEqual(result["draft_status"], "DRAFT")
        self.assertEqual(result["draft_post_id"], "draft-1")
        service.posts.return_value.insert.assert_called_once()
        self.assertTrue(service.posts.return_value.insert.call_args.kwargs["isDraft"])

    def test_blogger_publish_promotes_existing_draft_without_duplicate(self):
        service = unittest.mock.Mock()
        service.posts.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "draft-1",
                    "status": "DRAFT",
                    "customMetaData": '{"source_id":"source-1"}',
                    "url": "https://example.blogspot.com/draft",
                }
            ]
        }
        service.posts.return_value.publish.return_value.execute.return_value = {
            "id": "draft-1",
            "status": "LIVE",
            "url": "https://example.blogspot.com/live",
        }

        with (
            patch.dict("os.environ", {"BLOGGER_BLOG_ID": "blog-id"}, clear=True),
            patch.object(blogger, "get_service", return_value=service),
        ):
            result = blogger.publish_post(
                "শিরোনাম",
                "<p>খবর</p>",
                source_id="source-1",
                is_draft=False,
            )

        self.assertEqual(result["status"], "LIVE")
        self.assertEqual(result["url"], "https://example.blogspot.com/live")
        service.posts.return_value.list.assert_called_once_with(
            blogId="blog-id",
            status=["DRAFT", "LIVE"],
            maxResults=100,
            fetchBodies=True,
            pageToken=None,
        )
        service.posts.return_value.publish.assert_called_once_with(
            blogId="blog-id",
            postId="draft-1",
        )
        service.posts.return_value.insert.assert_not_called()

    def test_region_priority_and_major_emergency(self):
        west_bengal = {"category": "abp_kolkata", "title": "Local civic update"}
        national_emergency = {"category": "abp_india", "title": "Major earthquake emergency"}
        minor_world = {"category": "abp_world", "title": "New museum exhibition opens"}

        self.assertGreater(pipeline.rank_story(west_bengal), pipeline.rank_story(minor_world))
        self.assertGreater(pipeline.rank_story(national_emergency), pipeline.rank_story(west_bengal))

    def test_irrelevant_story_is_filtered(self):
        story = {"category": "abp_home", "title": "আজকের রাশিফল ও ভাগ্যফল"}

        self.assertIsNone(pipeline.rank_story(story))

    def test_duplicate_detection_uses_canonical_url_and_published_headline(self):
        existing = [{
            "link": "https://news.example/story/?utm_source=rss",
            "title": "প্রথম শিরোনাম",
            "article": {"headline": "কলকাতার নতুন সংবাদ শিরোনাম"},
        }]

        self.assertTrue(is_duplicate({"link": "https://news.example/story", "title": "অন্য লেখা"}, existing))
        self.assertTrue(is_duplicate({"link": "https://other.example/story", "title": "কলকাতার নতুন সংবাদ শিরোনাম"}, existing))

    def test_queue_preparation_deduplicates_a_batch_of_stories(self):
        stories = [
            {
                "category": "abp_kolkata",
                "title": "কলকাতার প্রথম গুরুত্বপূর্ণ খবর",
                "link": "https://news.example/story?utm_source=rss",
            },
            {
                "category": "abp_kolkata",
                "title": "কলকাতার প্রথম গুরুত্বপূর্ণ খবর",
                "link": "https://news.example/story",
            },
        ]

        queue = pipeline._prepare_queue([], stories)

        self.assertEqual(len(queue), 1)

    def test_html_sanitizer_removes_scripts_and_attributes(self):
        result = pipeline.sanitize_article('<p onclick="bad()">সংবাদ</p><script>secret()</script><a href="https://bad">লিংক</a>')

        self.assertEqual(result, "<p>সংবাদ</p>লিংক")
        self.assertNotIn("bad", result)

    def test_live_publication_requires_explicit_approval(self):
        cases = [
            ({}, False),
            ({"NEWS_PUBLISHING_ENABLED": "true", "GITHUB_EVENT_NAME": "schedule"}, True),
            ({"NEWS_PUBLISHING_ENABLED": "true", "GITHUB_EVENT_NAME": "workflow_dispatch"}, False),
            ({"NEWS_PUBLISHING_ENABLED": "true", "GITHUB_EVENT_NAME": "workflow_dispatch", "PUBLISH_REQUESTED": "true"}, True),
            ({"NEWS_PUBLISHING_ENABLED": "false", "GITHUB_EVENT_NAME": "schedule"}, False),
        ]
        for values, expected in cases:
            with self.subTest(values=values), patch.dict("os.environ", values, clear=True):
                self.assertEqual(pipeline._publication_approved(), expected)

    def test_successful_blogger_publication_precedes_facebook(self):
        item = {
            "source_id": "source-1",
            "status": "ready",
            "priority_score": 300,
            "article": {
                "headline": "বাংলা সংবাদ শিরোনাম",
                "article_html": "<p>তথ্যভিত্তিক সংবাদ প্রতিবেদন</p>",
                "labels": ["কলকাতা"],
                "seo_description": "কলকাতার গুরুত্বপূর্ণ সংবাদ",
                "facebook_caption": "বাংলা সংবাদ। Padma Bangla News-কে ফলো করুন",
            },
        }
        order = []

        def publish_blog(*args, **kwargs):
            order.append("blogger")
            return {
                "id": "post-1",
                "url": "https://example.blogspot.com/post.html",
                "title": args[0],
                "status": "LIVE",
            }

        def publish_page(page_id, caption, article_url):
            order.append("facebook")
            self.assertEqual(article_url, "https://example.blogspot.com/post.html")
            return "facebook-1", False

        environment = {
            "NEWS_PUBLISHING_ENABLED": "true",
            "GITHUB_EVENT_NAME": "schedule",
            "BLOGGER_BLOG_ID": "blog",
            "BLOGGER_CLIENT_ID": "client",
            "BLOGGER_CLIENT_SECRET": "secret",
            "BLOGGER_REFRESH_TOKEN": "refresh",
            "FACEBOOK_PAGE_ID": "page",
            "FACEBOOK_PAGE_ACCESS_TOKEN": "token",
        }
        with (
            patch.dict("os.environ", environment, clear=True),
            patch.object(pipeline, "load_queue", return_value=[item]),
            patch.object(pipeline, "_collect_stories", return_value=[]),
            patch.object(pipeline, "save_queue"),
            patch.object(pipeline, "count_published_today", return_value=0),
            patch.object(pipeline, "upload_news_image", return_value="https://res.cloudinary.com/test/image/upload/a.jpg"),
            patch.object(pipeline, "publish_post", side_effect=publish_blog),
            patch.object(pipeline, "publish_facebook", side_effect=publish_page),
        ):
            pipeline.run_pipeline()

        self.assertEqual(order, ["blogger", "facebook"])
        self.assertEqual(item["status"], "published")

    def test_unapproved_pipeline_creates_blogger_draft_only(self):
        item = {
            "source_id": "source-draft",
            "status": "ready",
            "priority_score": 300,
            "article": {
                "headline": "বাংলা সংবাদ শিরোনাম",
                "article_html": "<p>তথ্যভিত্তিক সংবাদ প্রতিবেদন</p>",
                "labels": ["কলকাতা"],
            },
        }
        environment = {
            "NEWS_PUBLISHING_ENABLED": "false",
            "BLOGGER_BLOG_ID": "blog",
            "BLOGGER_CLIENT_ID": "client",
            "BLOGGER_CLIENT_SECRET": "secret",
            "BLOGGER_REFRESH_TOKEN": "refresh",
        }
        with (
            patch.dict("os.environ", environment, clear=True),
            patch.object(pipeline, "load_queue", return_value=[item]),
            patch.object(pipeline, "_collect_stories", return_value=[]),
            patch.object(pipeline, "save_queue"),
            patch.object(pipeline, "upload_news_image", return_value="https://res.cloudinary.com/test/image/upload/a.jpg"),
            patch.object(
                pipeline,
                "publish_post",
                return_value={"id": "draft-1", "status": "DRAFT"},
            ) as create_blog,
            patch.object(pipeline, "publish_facebook") as publish_page,
        ):
            pipeline.run_pipeline()

        self.assertEqual(item["status"], "drafted")
        self.assertEqual(item["blogger_draft_id"], "draft-1")
        create_blog.assert_called_once()
        self.assertTrue(create_blog.call_args.kwargs["is_draft"])
        publish_page.assert_not_called()

    def test_approved_pipeline_promotes_draft_before_facebook(self):
        item = {
            "source_id": "source-draft",
            "status": "drafted",
            "priority_score": 300,
            "cloudinary_image_url": "https://res.cloudinary.com/test/image/upload/a.jpg",
            "blogger_draft_id": "draft-1",
            "article": {
                "headline": "বাংলা সংবাদ শিরোনাম",
                "article_html": "<p>তথ্যভিত্তিক সংবাদ প্রতিবেদন</p>",
                "labels": ["কলকাতা"],
                "facebook_caption": "বাংলা সংবাদ। Padma Bangla News-কে ফলো করুন",
            },
        }
        order = []

        def publish_blog(*args, **kwargs):
            order.append("blogger")
            self.assertFalse(kwargs["is_draft"])
            return {
                "id": "post-1",
                "url": "https://example.blogspot.com/post.html",
                "status": "LIVE",
            }

        def publish_page(page_id, caption, article_url):
            order.append("facebook")
            self.assertEqual(article_url, "https://example.blogspot.com/post.html")
            return "facebook-1", False

        environment = {
            "NEWS_PUBLISHING_ENABLED": "true",
            "GITHUB_EVENT_NAME": "workflow_dispatch",
            "PUBLISH_REQUESTED": "true",
            "BLOGGER_BLOG_ID": "blog",
            "BLOGGER_CLIENT_ID": "client",
            "BLOGGER_CLIENT_SECRET": "secret",
            "BLOGGER_REFRESH_TOKEN": "refresh",
            "FACEBOOK_PAGE_ID": "page",
            "FACEBOOK_PAGE_ACCESS_TOKEN": "token",
        }
        with (
            patch.dict("os.environ", environment, clear=True),
            patch.object(pipeline, "load_queue", return_value=[item]),
            patch.object(pipeline, "_collect_stories", return_value=[]),
            patch.object(pipeline, "save_queue"),
            patch.object(pipeline, "count_published_today", return_value=0),
            patch.object(pipeline, "publish_post", side_effect=publish_blog),
            patch.object(pipeline, "publish_facebook", side_effect=publish_page),
        ):
            pipeline.run_pipeline()

        self.assertEqual(order, ["blogger", "facebook"])
        self.assertEqual(item["status"], "published")

    def test_facebook_is_skipped_when_blogger_fails(self):
        item = {
            "source_id": "source-2",
            "status": "ready",
            "priority_score": 300,
            "article": {"headline": "শিরোনাম", "article_html": "<p>খবর</p>"},
        }
        environment = {
            "NEWS_PUBLISHING_ENABLED": "true",
            "GITHUB_EVENT_NAME": "schedule",
            "BLOGGER_BLOG_ID": "blog",
            "BLOGGER_CLIENT_ID": "client",
            "BLOGGER_CLIENT_SECRET": "secret",
            "BLOGGER_REFRESH_TOKEN": "refresh",
            "FACEBOOK_PAGE_ID": "page",
            "FACEBOOK_PAGE_ACCESS_TOKEN": "token",
        }
        with (
            patch.dict("os.environ", environment, clear=True),
            patch.object(pipeline, "load_queue", return_value=[item]),
            patch.object(pipeline, "_collect_stories", return_value=[]),
            patch.object(pipeline, "save_queue"),
            patch.object(pipeline, "count_published_today", return_value=0),
            patch.object(pipeline, "upload_news_image", return_value="https://res.cloudinary.com/test/image/upload/a.jpg"),
            patch.object(pipeline, "publish_post", side_effect=RuntimeError("network")),
            patch.object(pipeline, "publish_facebook") as publish_page,
        ):
            pipeline.run_pipeline()

        publish_page.assert_not_called()

    def test_missing_facebook_credentials_leave_blogger_post_pending(self):
        item = {
            "source_id": "source-3",
            "status": "ready",
            "priority_score": 300,
            "article": {"headline": "শিরোনাম", "article_html": "<p>খবর</p>"},
        }
        environment = {
            "NEWS_PUBLISHING_ENABLED": "true",
            "GITHUB_EVENT_NAME": "schedule",
            "BLOGGER_BLOG_ID": "blog",
            "BLOGGER_CLIENT_ID": "client",
            "BLOGGER_CLIENT_SECRET": "secret",
            "BLOGGER_REFRESH_TOKEN": "refresh",
        }
        with (
            patch.dict("os.environ", environment, clear=True),
            patch.object(pipeline, "load_queue", return_value=[item]),
            patch.object(pipeline, "_collect_stories", return_value=[]),
            patch.object(pipeline, "save_queue"),
            patch.object(pipeline, "count_published_today", return_value=0),
            patch.object(pipeline, "upload_news_image", return_value="https://res.cloudinary.com/test/image/upload/a.jpg"),
            patch.object(
                pipeline,
                "publish_post",
                return_value={
                    "id": "post-3",
                    "url": "https://example.blogspot.com/post.html",
                    "status": "LIVE",
                },
            ),
            patch.object(pipeline, "publish_facebook") as publish_page,
        ):
            pipeline.run_pipeline()

        self.assertEqual(item["status"], "facebook_pending")
        self.assertEqual(item["blogger_url"], "https://example.blogspot.com/post.html")
        publish_page.assert_not_called()

    def test_daily_cap_counts_kolkata_publications(self):
        rows = [
            {"blogger_published_at": "2026-10-09T06:00:00+00:00"},
            {"blogger_published_at": "2026-10-08T06:00:00+00:00"},
            {"status": "ready"},
        ]

        self.assertEqual(pipeline.published_today(rows, today=date(2026, 10, 9)), 1)


if __name__ == "__main__":
    unittest.main()