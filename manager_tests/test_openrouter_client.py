import json
import unittest
from unittest.mock import patch
from manager.openrouter_client import generate_bengali_draft


class FakeResponse:
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, size=-1): return self.data[:size]


def api_response(content):
    return json.dumps({"choices":[{"message":{"content":json.dumps(content,ensure_ascii=False)}}]}).encode()


class OpenRouterTests(unittest.TestCase):
    def setUp(self):
        self.story = {"title":"কলকাতায় নতুন প্রকল্প", "link":"https://example.org/story", "description":"প্রদত্ত তথ্য", "source":"Demo"}

    def test_requires_key_without_network(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "OPENROUTER_API_KEY"):
                generate_bengali_draft(self.story)

    def test_requires_model_without_network(self):
        with patch.dict("os.environ", {"OPENROUTER_API_KEY":"test-key"}, clear=True):
            with self.assertRaisesRegex(ValueError, "OPENROUTER_MODEL"):
                generate_bengali_draft(self.story)

    def test_mocked_response_is_draft_candidate(self):
        draft = {"title":"খসড়া", "body":"প্রদত্ত তথ্যের ভিত্তিতে খসড়া।", "summary":"সংক্ষিপ্তসার", "verification_notes":["যাচাই করুন"]}
        def fake_opener(request, timeout): return FakeResponse(api_response(draft))
        result = generate_bengali_draft(self.story, api_key="test-key", model="test/model", opener=fake_opener)
        self.assertEqual(result["status"], "draft_candidate")
        self.assertFalse(result["published"])
        self.assertEqual(result["source_url"], self.story["link"])

    def test_rejects_missing_source_link(self):
        with self.assertRaises(ValueError):
            generate_bengali_draft({"title":"খবর"}, api_key="x", model="test/model")

    def test_rejects_bad_model_json(self):
        def fake_opener(request, timeout):
            return FakeResponse(json.dumps({"choices":[{"message":{"content":"not json"}}]}).encode())
        with self.assertRaisesRegex(ValueError, "JSON object"):
            generate_bengali_draft(self.story, api_key="x", model="test/model", opener=fake_opener)


if __name__ == "__main__": unittest.main()
