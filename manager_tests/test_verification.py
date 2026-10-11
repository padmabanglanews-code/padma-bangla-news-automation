import unittest
from manager.verification import verify_draft, verify_draft_candidates


class DraftVerificationTests(unittest.TestCase):
    def good_draft(self):
        return {
            "title": "কলকাতায় নতুন উন্নয়ন প্রকল্পের ঘোষণা",
            "body": ("প্রশাসনের পক্ষ থেকে নতুন প্রকল্পের কথা জানানো হয়েছে। "
                     "প্রকল্পের বিস্তারিত তথ্য ও বাস্তবায়নের সময়সূচি নিয়ে সংশ্লিষ্ট দপ্তর "
                     "আরও তথ্য দিয়েছে। প্রকাশের আগে মূল সূত্র মিলিয়ে তথ্য যাচাই করা প্রয়োজন।"),
            "summary": "কলকাতায় নতুন প্রকল্প নিয়ে প্রশাসনের ঘোষণা প্রকাশিত হয়েছে।",
            "source_url": "https://example.org/news",
            "verification_notes": "মূল প্রতিবেদনের সঙ্গে তথ্য মিলিয়ে দেখতে হবে",
        }

    def test_valid_structure_passes_but_fact_check_is_not_claimed(self):
        report = verify_draft(self.good_draft())
        self.assertTrue(report["passed"])
        self.assertFalse(report["checks"]["factual_accuracy_verified"])
        self.assertFalse(report["published"])

    def test_missing_fields_fail(self):
        report = verify_draft({})
        self.assertFalse(report["passed"])
        self.assertIn("title_too_short", report["errors"])
        self.assertIn("missing_source_url", report["errors"])

    def test_invalid_source_url_fails(self):
        draft = self.good_draft()
        draft["source_url"] = "javascript:alert(1)"
        self.assertIn("invalid_source_url", verify_draft(draft)["errors"])

    def test_placeholder_text_fails(self):
        draft = self.good_draft()
        draft["body"] += " lorem ipsum"
        self.assertIn("placeholder_or_ai_meta_text", verify_draft(draft)["errors"])

    def test_devanagari_mixed_into_bengali_draft_fails(self):
        draft = self.good_draft()
        draft["body"] += " प्रधानमंत्री"
        report = verify_draft(draft)
        self.assertFalse(report["passed"])
        self.assertIn("non_bengali_devanagari_script", report["errors"])

    def test_non_bengali_body_fails(self):
        draft = self.good_draft()
        draft["title"] = "Breaking News Update"
        draft["body"] = "This is an English-only body with enough length. " * 4
        report = verify_draft(draft)
        self.assertFalse(report["passed"])
        self.assertIn("bengali_script_missing", report["errors"])

    def test_missing_verification_notes_warns(self):
        draft = self.good_draft()
        del draft["verification_notes"]
        self.assertIn("human_fact_check_required", verify_draft(draft)["warnings"])

    def test_batch_report_does_not_publish(self):
        result = verify_draft_candidates([self.good_draft(), {}])
        self.assertEqual(result["passed_count"], 1)
        self.assertEqual(result["needs_revision_count"], 1)
        self.assertFalse(result["published"])


if __name__ == "__main__":
    unittest.main()
