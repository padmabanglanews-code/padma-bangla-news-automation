import unittest
from manager.dashboard_readonly import build_dashboard_snapshot


def draft(title="কলকাতায় নতুন প্রকল্পের ঘোষণা"):
    return {
        "id": "news-1",
        "title": title,
        "body": ("প্রশাসনের পক্ষ থেকে নতুন প্রকল্পের কথা জানানো হয়েছে। "
                 "প্রকল্পের বিস্তারিত তথ্য ও বাস্তবায়নের সময়সূচি নিয়ে সংশ্লিষ্ট দপ্তর "
                 "আরও তথ্য দিয়েছে। প্রকাশের আগে মূল সূত্র মিলিয়ে তথ্য যাচাই করা প্রয়োজন।"),
        "summary": "কলকাতায় নতুন প্রকল্প নিয়ে প্রশাসনের ঘোষণা প্রকাশিত হয়েছে।",
        "source_url": "https://example.org/news",
        "verification_notes": "মূল সূত্র মিলিয়ে দেখতে হবে",
    }


class ReadOnlyDashboardTests(unittest.TestCase):
    def test_empty_snapshot(self):
        result = build_dashboard_snapshot()
        self.assertEqual(result["draft_count"], 0)
        self.assertTrue(result["read_only"])
        self.assertFalse(result["published"])

    def test_snapshot_contains_safe_quality_summary(self):
        result = build_dashboard_snapshot([draft()], pipeline_status={"state":"idle","last_run":"test"})
        self.assertEqual(result["draft_count"], 1)
        self.assertEqual(result["pending_review_count"], 1)
        self.assertTrue(result["drafts"][0]["quality_passed"])
        self.assertFalse(result["drafts"][0]["published"])
        self.assertEqual(result["pipeline_status"]["state"], "idle")

    def test_invalid_draft_is_shown_as_needs_revision(self):
        result = build_dashboard_snapshot([{"id":"bad","title":"x"}])
        self.assertFalse(result["drafts"][0]["quality_passed"])
        self.assertEqual(result["drafts"][0]["quality_status"], "needs_revision")

    def test_does_not_mutate_input(self):
        source = draft()
        build_dashboard_snapshot([source])
        self.assertNotIn("quality_report", source)

    def test_non_dictionary_rows_are_skipped(self):
        result = build_dashboard_snapshot([None, "bad", draft()])
        self.assertEqual(result["draft_count"], 1)

    def test_snapshot_never_reports_published(self):
        source = draft()
        source["published"] = True
        result = build_dashboard_snapshot([source])
        self.assertFalse(result["drafts"][0]["published"])
        self.assertFalse(result["published"])


if __name__ == "__main__":
    unittest.main()
