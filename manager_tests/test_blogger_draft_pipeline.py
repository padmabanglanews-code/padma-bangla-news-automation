import unittest
from manager.draft_pipeline import generate_draft_candidates


class BloggerBoundaryTests(unittest.TestCase):
    def test_draft_candidates_do_not_call_blogger(self):
        calls = []
        def generator(story):
            calls.append(story)
            return {"title":"খসড়া","body":"লেখা","summary":"সারাংশ","published":False}
        result = generate_draft_candidates([{"title":"খবর","link":"https://example.org"}], generator=generator)
        self.assertEqual(len(calls), 1)
        self.assertFalse(result["published"])
        self.assertFalse(result["blogger_contacted"])


if __name__ == "__main__": unittest.main()
