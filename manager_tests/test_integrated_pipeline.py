import unittest
from manager.integrated_pipeline import run_integrated_pipeline


def fake_story_xml():
    return """<?xml version="1.0"?><rss version="2.0"><channel><title>Test</title>
    <item><title>কলকাতায় নতুন উন্নয়ন প্রকল্পের ঘোষণা</title>
    <link>https://example.org/news-1</link><description>প্রশাসন নতুন প্রকল্পের বিস্তারিত তথ্য প্রকাশ করেছে।</description>
    <pubDate>Sun, 11 Oct 2026 08:00:00 +0530</pubDate></item></channel></rss>"""


def fake_draft(story):
    return {
        "title": "কলকাতায় নতুন উন্নয়ন প্রকল্পের ঘোষণা",
        "body": ("প্রশাসনের পক্ষ থেকে নতুন প্রকল্পের কথা জানানো হয়েছে। "
                 "প্রকল্পের বিস্তারিত তথ্য ও বাস্তবায়নের সময়সূচি নিয়ে সংশ্লিষ্ট দপ্তর "
                 "আরও তথ্য দিয়েছে। প্রকাশের আগে মূল সূত্র মিলিয়ে তথ্য যাচাই করা প্রয়োজন।"),
        "summary": "কলকাতায় নতুন প্রকল্প নিয়ে প্রশাসনের ঘোষণা প্রকাশিত হয়েছে।",
        "source_url": story["link"],
        "verification_notes": "মূল সূত্রের সঙ্গে মিলিয়ে দেখতে হবে",
    }


class IntegratedPipelineTests(unittest.TestCase):
    def test_defaults_are_idle_and_do_not_call_dependencies(self):
        result = run_integrated_pipeline()
        self.assertEqual(result["mode"], "integration-safe-idle")
        self.assertFalse(result["published"])
        self.assertFalse(result["blogger_contacted"])

    def test_rejects_ai_without_explicit_rss(self):
        with self.assertRaisesRegex(ValueError, "generate_ai_requires_live_rss"):
            run_integrated_pipeline(generate_ai=True)

    def test_rejects_blogger_without_ai(self):
        with self.assertRaisesRegex(ValueError, "requires_generate_ai"):
            run_integrated_pipeline(create_blogger_drafts=True)

    def test_mock_integrated_flow_never_publishes(self):
        blogger_calls = []
        def fetcher(url):
            return fake_story_xml()
        def blogger_creator(draft):
            blogger_calls.append(draft)
            return {"status":"draft_created","blogger_contacted":True,"published":False}
        result = run_integrated_pipeline(
            live_rss=True, generate_ai=True, create_blogger_drafts=True,
            sources_path="manager/feed_sources.json", rss_fetcher=fetcher,
            ai_generator=fake_draft, blogger_creator=blogger_creator, max_stories=1,
        )
        self.assertEqual(len(result["ai_draft_candidates"]), 1)
        self.assertTrue(result["quality"]["reports"][0]["passed"])
        self.assertEqual(len(blogger_calls), 1)
        self.assertTrue(result["blogger_contacted"])
        self.assertFalse(result["published"])
        self.assertFalse(result["blogger_results"][0]["published"])

    def test_quality_failure_prevents_blogger_call(self):
        blogger_calls = []
        result = run_integrated_pipeline(
            live_rss=True, generate_ai=True, create_blogger_drafts=True,
            rss_fetcher=lambda url: fake_story_xml(),
            ai_generator=lambda story: {"title":"খারাপ"},
            blogger_creator=lambda draft: blogger_calls.append(draft),
            max_stories=1,
        )
        self.assertEqual(blogger_calls, [])
        self.assertEqual(result["blogger_results"][0]["status"], "skipped_quality_failed")
        self.assertFalse(result["published"])


if __name__ == "__main__":
    unittest.main()
