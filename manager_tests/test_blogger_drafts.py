import json
import unittest
from unittest.mock import patch
from manager.blogger_drafts import create_blogger_draft


class FakeResponse:
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, size=-1): return self.data[:size]


class BloggerDraftTests(unittest.TestCase):
    def test_requires_token_without_network(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "BLOGGER_ACCESS_TOKEN"):
                create_blogger_draft({"title":"খসড়া","body":"লেখা"})

    def test_requires_blog_id_without_network(self):
        with patch.dict("os.environ", {"BLOGGER_ACCESS_TOKEN":"test-token"}, clear=True):
            with self.assertRaisesRegex(ValueError, "BLOGGER_BLOG_ID"):
                create_blogger_draft({"title":"খসড়া","body":"লেখা"})

    def test_mocked_insert_forces_is_draft_true(self):
        seen = {}
        def fake_opener(request, timeout):
            seen["url"] = request.full_url
            seen["method"] = request.get_method()
            seen["payload"] = json.loads(request.data.decode())
            return FakeResponse(json.dumps({"id":"123","title":"খসড়া"}, ensure_ascii=False).encode("utf-8"))
        result = create_blogger_draft({"title":"খসড়া","body":"লেখা"}, access_token="test-token", blog_id="456", opener=fake_opener)
        self.assertIn("isDraft=true", seen["url"])
        self.assertEqual(seen["method"], "POST")
        self.assertEqual(result["status"], "draft_created")
        self.assertFalse(result["published"])

    def test_rejects_empty_content(self):
        with self.assertRaises(ValueError):
            create_blogger_draft({"title":"খসড়া","body":""}, access_token="x", blog_id="1")

    def test_bad_response_not_confirmed(self):
        def fake_opener(request, timeout): return FakeResponse(json.dumps({"title":"no id"}, ensure_ascii=False).encode("utf-8"))
        with self.assertRaisesRegex(ValueError, "did not confirm"):
            create_blogger_draft({"title":"খসড়া","body":"লেখা"}, access_token="x", blog_id="1", opener=fake_opener)


if __name__ == "__main__": unittest.main()
