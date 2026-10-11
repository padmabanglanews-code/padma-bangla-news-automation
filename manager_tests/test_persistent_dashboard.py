import json
import tempfile
import unittest
from pathlib import Path

from manager.dashboard_api import DashboardAPIError
from manager.persistent_dashboard import PersistentDashboardDraftStore


def valid_draft():
    return {
        "title": "কলকাতায় নতুন উন্নয়ন প্রকল্পের ঘোষণা",
        "body": ("প্রশাসনের পক্ষ থেকে নতুন প্রকল্পের কথা জানানো হয়েছে। "
                 "প্রকল্পের বিস্তারিত তথ্য ও বাস্তবায়নের সময়সূচি নিয়ে সংশ্লিষ্ট দপ্তর "
                 "আরও তথ্য দিয়েছে। প্রকাশের আগে মূল সূত্র মিলিয়ে তথ্য যাচাই করা প্রয়োজন।"),
        "summary": "কলকাতায় নতুন প্রকল্প নিয়ে প্রশাসনের ঘোষণা প্রকাশিত হয়েছে।",
        "source_url": "https://example.org/news",
        "verification_notes": "মূল সূত্রের সঙ্গে মিলিয়ে দেখতে হবে",
    }


class PersistentDashboardTests(unittest.TestCase):
    def test_draft_survives_store_recreation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drafts.json"
            first = PersistentDashboardDraftStore(path)
            first.add_draft(valid_draft(), draft_id="news-1")
            second = PersistentDashboardDraftStore(path)
            self.assertEqual(second.get_draft("news-1")["review_status"], "pending_review")
            self.assertFalse(second.get_draft("news-1")["published"])

    def test_review_survives_store_recreation_without_publishing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drafts.json"
            store = PersistentDashboardDraftStore(path)
            store.add_draft(valid_draft(), draft_id="news-1")
            store.review_draft("news-1", decision="approve", reviewer_note="মানব যাচাই বাকি")
            reopened = PersistentDashboardDraftStore(path)
            result = reopened.get_draft("news-1")
            self.assertEqual(result["review_status"], "approved_for_manual_next_step")
            self.assertFalse(result["published"])

    def test_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersistentDashboardDraftStore(Path(directory) / "drafts.json")
            store.add_draft(valid_draft(), draft_id="news-1")
            with self.assertRaisesRegex(DashboardAPIError, "duplicate"):
                store.add_draft(valid_draft(), draft_id="news-1")

    def test_corrupt_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drafts.json"
            path.write_text("{", encoding="utf-8")
            store = PersistentDashboardDraftStore(path)
            with self.assertRaisesRegex(DashboardAPIError, "unreadable"):
                store.list_drafts()
            self.assertEqual(path.read_text(encoding="utf-8"), "{")

    def test_invalid_quality_cannot_be_approved_and_is_not_written_as_approved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drafts.json"
            store = PersistentDashboardDraftStore(path)
            store.add_draft({"title": "bad"}, draft_id="bad-1")
            with self.assertRaisesRegex(DashboardAPIError, "quality_check_failed"):
                store.review_draft("bad-1", decision="approve")
            self.assertEqual(store.get_draft("bad-1")["review_status"], "pending_review")


if __name__ == "__main__":
    unittest.main()
