import os
import unittest
from unittest.mock import patch

from nanoclaw_recipe.nanoclaw import compute_final_answer_bonus, compute_score


class TestFinalAnswerBonus(unittest.TestCase):
    def test_bonus_is_awarded_for_nonempty_completed_answer(self):
        result = compute_final_answer_bonus(
            {
                "rollout_termination_reason": "completed_no_tool_call",
                "rollout_final_answer": "Done.",
            },
            {},
            "decoded trajectory",
            enabled=True,
            score=0.05,
        )

        self.assertEqual(
            result,
            {
                "nanoclaw_has_final_answer": True,
                "nanoclaw_final_answer_bonus_enabled": True,
                "nanoclaw_final_answer_bonus_score": 0.05,
                "nanoclaw_final_answer_bonus_awarded": 0.05,
            },
        )

    def test_bonus_is_not_awarded_for_empty_or_incomplete_answer(self):
        empty_result = compute_final_answer_bonus(
            {
                "rollout_termination_reason": "completed_no_tool_call",
                "rollout_final_answer": "   ",
            },
            {},
            "decoded trajectory",
            enabled=True,
            score=0.05,
        )
        exhausted_result = compute_final_answer_bonus(
            {
                "rollout_termination_reason": "max_response_tokens",
                "rollout_final_answer": "Looks final, but the rollout exhausted its budget.",
            },
            {},
            "decoded trajectory",
            enabled=True,
            score=0.05,
        )

        self.assertFalse(empty_result["nanoclaw_has_final_answer"])
        self.assertEqual(empty_result["nanoclaw_final_answer_bonus_awarded"], 0.0)
        self.assertFalse(exhausted_result["nanoclaw_has_final_answer"])
        self.assertEqual(exhausted_result["nanoclaw_final_answer_bonus_awarded"], 0.0)

    def test_bonus_reads_environment(self):
        with patch.dict(
            os.environ,
            {
                "NANOCLAW_FINAL_ANSWER_BONUS_ENABLE": "True",
                "NANOCLAW_FINAL_ANSWER_BONUS_SCORE": "0.125",
            },
        ):
            result = compute_final_answer_bonus(
                {"rollout_termination_reason": "completed_no_tool_call"},
                {},
                "Backward-compatible final answer.",
            )

        self.assertTrue(result["nanoclaw_has_final_answer"])
        self.assertTrue(result["nanoclaw_final_answer_bonus_enabled"])
        self.assertEqual(result["nanoclaw_final_answer_bonus_score"], 0.125)
        self.assertEqual(result["nanoclaw_final_answer_bonus_awarded"], 0.125)

    def test_explicit_disable_overrides_environment(self):
        with patch.dict(
            os.environ,
            {
                "NANOCLAW_FINAL_ANSWER_BONUS_ENABLE": "True",
                "NANOCLAW_FINAL_ANSWER_BONUS_SCORE": "0.125",
            },
        ):
            result = compute_final_answer_bonus(
                {
                    "rollout_termination_reason": "completed_no_tool_call",
                    "rollout_final_answer": "Done.",
                },
                {},
                "decoded trajectory",
                enabled=False,
                score=0.5,
            )

        self.assertTrue(result["nanoclaw_has_final_answer"])
        self.assertFalse(result["nanoclaw_final_answer_bonus_enabled"])
        self.assertEqual(result["nanoclaw_final_answer_bonus_score"], 0.5)
        self.assertEqual(result["nanoclaw_final_answer_bonus_awarded"], 0.0)

    def test_compute_score_can_reward_final_answer_without_requiring_it(self):
        result = compute_score(
            data_source="nanoclaw/test",
            solution_str="Done.",
            ground_truth={"task_id": "test"},
            extra_info={
                "rollout_termination_reason": "completed_no_tool_call",
                "rollout_final_answer": "Done.",
            },
            require_final_answer=False,
            final_answer_bonus_enable=True,
            final_answer_bonus_score=0.05,
            score_uninitialized_workspace=False,
        )

        self.assertAlmostEqual(result["score"], 0.05)
        self.assertEqual(result["nanoclaw_status"], "no_workspace")
        self.assertTrue(result["nanoclaw_has_final_answer"])
        self.assertAlmostEqual(result["nanoclaw_final_answer_bonus_awarded"], 0.05)

    def test_require_final_answer_still_rejects_incomplete_rollout(self):
        result = compute_score(
            data_source="nanoclaw/test",
            solution_str="Partial trajectory text.",
            ground_truth={"task_id": "test"},
            extra_info={"rollout_termination_reason": "max_response_tokens"},
            require_final_answer=True,
            final_answer_bonus_enable=True,
            final_answer_bonus_score=0.05,
            score_uninitialized_workspace=False,
        )

        self.assertAlmostEqual(result["score"], 0.0)
        self.assertEqual(result["nanoclaw_status"], "missing_final_answer")
        self.assertFalse(result["nanoclaw_has_final_answer"])
        self.assertAlmostEqual(result["nanoclaw_final_answer_bonus_awarded"], 0.0)


if __name__ == "__main__":
    unittest.main()
