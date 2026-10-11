import unittest
from manager.draft_pipeline import generate_draft_candidates


class DraftPipelineTests(unittest.TestCase):
    def test_uses_mock_generator_and_never_publishes(self):
        stories = [{"title":"খবর","link":"https://example.org/a"}]
        result = generate_draft_candidates(stories, generator=lambda s: {
            "title":"খসড়া","body":"বডি","summary":"সারাংশ","source_url":s["link"],
            "status":"draft_candidate","published":False
        })
        self.assertEqual(len(result["candidates"]), 1)
        self.assertFalse(result["published"])
        self.assertFalse(result["blogger_contacted"])

    def test_generator_error_is_reported(self):
        result = generate_draft_candidates([{"link":"https://example.org/a"}],
            generator=lambda s: (_ for _ in ()).throw(ValueError("missing credentials")))
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["candidates"], [])


if __name__ == "__main__": unittest.main()
