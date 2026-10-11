import unittest

from manager.dashboard_api import DashboardAPIError
from manager.supabase_dashboard import SupabaseDashboardDraftStore


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


class Response:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, table):
        self.table = table
        self.filters = {}

    def select(self, *_args):
        return self

    def order(self, *_args):
        return self

    def limit(self, *_args):
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def insert(self, row):
        if row["id"] in self.table.rows:
            raise ValueError("duplicate")
        self.table.rows[row["id"]] = dict(row)
        return self

    def update(self, values):
        self.values = dict(values)
        return self

    def execute(self):
        if hasattr(self, "values"):
            for row in self.table.rows.values():
                if all(row.get(k) == v for k, v in self.filters.items()):
                    row.update(self.values)
            return Response([])
        rows = list(self.table.rows.values())
        rows = [r for r in rows if all(r.get(k) == v for k, v in self.filters.items())]
        return Response(rows)


class FakeTable:
    def __init__(self):
        self.rows = {}

    def table(self, _name):
        return FakeQuery(self)


class SupabaseDashboardTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeTable()
        self.store = SupabaseDashboardDraftStore(client=self.client)

    def test_add_and_retrieve_stays_unpublished(self):
        result = self.store.add_draft(valid_draft(), draft_id="news-1")
        self.assertEqual(result["review_status"], "pending_review")
        self.assertFalse(result["published"])
        self.assertEqual(self.store.get_draft("news-1")["title"], valid_draft()["title"])

    def test_review_status_persists_without_publishing(self):
        self.store.add_draft(valid_draft(), draft_id="news-1")
        result = self.store.review_draft(
            "news-1", decision="approve", reviewer_note="সম্পাদকীয় যাচাই বাকি"
        )
        self.assertEqual(result["review_status"], "approved_for_manual_next_step")
        self.assertEqual(result["reviewer_note"], "সম্পাদকীয় যাচাই বাকি")
        self.assertFalse(result["published"])

    def test_invalid_quality_cannot_be_approved(self):
        self.store.add_draft({"title": "bad"}, draft_id="bad-1")
        with self.assertRaisesRegex(DashboardAPIError, "quality_check_failed"):
            self.store.review_draft("bad-1", decision="approve")
        self.assertEqual(self.store.get_draft("bad-1")["review_status"], "pending_review")

    def test_missing_id_returns_not_found(self):
        with self.assertRaisesRegex(DashboardAPIError, "draft_not_found"):
            self.store.get_draft("missing")


if __name__ == "__main__":
    unittest.main()
