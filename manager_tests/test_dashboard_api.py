import unittest
from manager.dashboard_api import DashboardAPIError, DashboardDraftStore


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


class DashboardDraftStoreTests(unittest.TestCase):
    def test_list_and_get_return_safe_pending_draft(self):
        store = DashboardDraftStore([valid_draft()])
        item = store.get_draft("draft-1")
        self.assertEqual(item["review_status"], "pending_review")
        self.assertFalse(item["published"])
        self.assertEqual(len(store.list_drafts()), 1)

    def test_approve_is_not_publish(self):
        store = DashboardDraftStore([valid_draft()])
        item = store.review_draft("draft-1", decision="approve", reviewer_note="Reviewed")
        self.assertEqual(item["review_status"], "approved_for_manual_next_step")
        self.assertFalse(item["published"])

    def test_reject_is_stored_without_publishing(self):
        store = DashboardDraftStore([valid_draft()])
        item = store.review_draft("draft-1", decision="reject")
        self.assertEqual(item["review_status"], "rejected")
        self.assertFalse(item["published"])

    def test_failed_quality_check_cannot_be_approved(self):
        store = DashboardDraftStore([{"title": "bad"}])
        with self.assertRaisesRegex(DashboardAPIError, "quality_check_failed"):
            store.review_draft("draft-1", decision="approve")

    def test_unknown_draft_and_invalid_decision_fail(self):
        store = DashboardDraftStore()
        with self.assertRaisesRegex(DashboardAPIError, "draft_not_found"):
            store.get_draft("missing")
        store = DashboardDraftStore([valid_draft()])
        with self.assertRaisesRegex(DashboardAPIError, "decision_must_be"):
            store.review_draft("draft-1", decision="publish")

    def test_duplicate_id_rejected(self):
        store = DashboardDraftStore([valid_draft()])
        with self.assertRaisesRegex(DashboardAPIError, "duplicate"):
            store.add_draft(valid_draft(), draft_id="draft-1")

    def test_review_is_one_time(self):
        store = DashboardDraftStore([valid_draft()])
        store.review_draft("draft-1", decision="reject")
        with self.assertRaisesRegex(DashboardAPIError, "already_reviewed"):
            store.review_draft("draft-1", decision="approve")


if __name__ == "__main__":
    unittest.main()
