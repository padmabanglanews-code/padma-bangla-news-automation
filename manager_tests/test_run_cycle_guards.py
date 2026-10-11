import os
import unittest
from unittest.mock import patch

from manager.run_cycle import _enabled


class RunCycleGuardTests(unittest.TestCase):
    def test_live_stages_default_off(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_enabled("PADMA_RUN_LIVE_RSS"))
            self.assertFalse(_enabled("PADMA_RUN_OPENROUTER"))
            self.assertFalse(_enabled("PADMA_CREATE_BLOGGER_DRAFTS"))

    def test_only_explicit_true_enables_flag(self):
        with patch.dict(os.environ, {"PADMA_RUN_OPENROUTER": "TRUE"}, clear=True):
            self.assertTrue(_enabled("PADMA_RUN_OPENROUTER"))
        with patch.dict(os.environ, {"PADMA_RUN_OPENROUTER": "1"}, clear=True):
            self.assertFalse(_enabled("PADMA_RUN_OPENROUTER"))


if __name__ == "__main__":
    unittest.main()
