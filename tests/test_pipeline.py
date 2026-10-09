import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import unittest
from datetime import date
from unittest.mock import patch

from dedupe import is_duplicate
import pipeline


class PipelineTests(unittest.TestCase):
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
            return {"id": "post-1", "url": "https://example.blogspot.com/post.html", "title": args[0]}

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
            patch.object(
                pipeline,
                "publish_post",
                return_value={"id": "post-3", "url": "https://example.blogspot.com/post.html"},
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