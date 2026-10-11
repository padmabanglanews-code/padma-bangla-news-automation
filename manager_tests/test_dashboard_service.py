import tempfile
import unittest
from pathlib import Path

from manager.dashboard_service import run_dashboard_cycle
from manager.persistent_dashboard import PersistentDashboardDraftStore


def draft(story):
    return {
        "title": "কলকাতায় নতুন উন্নয়ন প্রকল্পের ঘোষণা",
        "body": ("প্রশাসনের পক্ষ থেকে নতুন প্রকল্পের কথা জানানো হয়েছে। "
                 "প্রকল্পের বিস্তারিত তথ্য ও বাস্তবায়নের সময়সূচি নিয়ে সংশ্লিষ্ট দপ্তর "
                 "আরও তথ্য দিয়েছে। প্রকাশের আগে মূল সূত্র মিলিয়ে তথ্য যাচাই করা প্রয়োজন।"),
        "summary": "কলকাতায় নতুন প্রকল্প নিয়ে প্রশাসনের ঘোষণা প্রকাশিত হয়েছে।",
        "source_url": story["link"],
        "verification_notes": "মূল সূত্রের সঙ্গে মিলিয়ে দেখতে হবে",
    }


XML = """<?xml version="1.0"?><rss version="2.0"><channel><title>Test</title>
<item><title>কলকাতায় নতুন প্রকল্প</title><link>https://example.org/news</link>
<description>প্রশাসনের নতুন প্রকল্প সম্পর্কে প্রকাশিত তথ্য।</description>
<pubDate>Sun, 11 Oct 2026 08:00:00 +0530</pubDate></item></channel></rss>"""


class DashboardServiceTests(unittest.TestCase):
    def test_default_cycle_is_safe_idle(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersistentDashboardDraftStore(Path(directory) / "drafts.json")
            result = run_dashboard_cycle(store=store)
            self.assertEqual(result["pipeline"]["mode"], "integration-safe-idle")
            self.assertEqual(result["dashboard"]["draft_count"], 0)
            self.assertFalse(result["published"])

    def test_mock_cycle_persists_candidate_and_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersistentDashboardDraftStore(Path(directory) / "drafts.json")
            result = run_dashboard_cycle(
                live_rss=True, generate_ai=True,
                rss_fetcher=lambda url: XML,
                ai_generator=draft, store=store, max_stories=1,
            )
            self.assertEqual(result["dashboard"]["draft_count"], 1)
            self.assertEqual(result["dashboard"]["pending_review_count"], 1)
            self.assertEqual(len(result["saved_draft_ids"]), 1)
            self.assertFalse(result["published"])
            self.assertFalse(result["dashboard"]["drafts"][0]["published"])

    def test_repeated_cycle_does_not_duplicate_same_story(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersistentDashboardDraftStore(Path(directory) / "drafts.json")
            kwargs = dict(live_rss=True, generate_ai=True, rss_fetcher=lambda url: XML,
                          ai_generator=draft, store=store, max_stories=1)
            first = run_dashboard_cycle(**kwargs)
            second = run_dashboard_cycle(**kwargs)
            self.assertEqual(first["saved_draft_ids"], second["saved_draft_ids"])
            self.assertEqual(second["dashboard"]["draft_count"], 1)


if __name__ == "__main__":
    unittest.main()
