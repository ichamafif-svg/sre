from __future__ import annotations

import unittest

from control_plane.domain import Permission, PolicyAction
from control_plane.policy.opa import OpaPolicyEngine, fail_closed_decision


class OpaPolicyAdapterContractTest(unittest.TestCase):
    def test_parse_decision_requires_action_permissions(self) -> None:
        decision = OpaPolicyEngine._parse_decision(
            {
                "policy_version": "test",
                "permissions": {
                    "INVESTIGATE": "ALLOW",
                    "DEPLOY_PRODUCTION": "HUMAN",
                },
                "required_human_actions": ["DEPLOY_PRODUCTION"],
                "blocked_reasons": [],
            }
        )

        self.assertEqual(decision.permission_for(PolicyAction.INVESTIGATE), Permission.ALLOW)
        self.assertEqual(decision.permission_for(PolicyAction.DEPLOY_PRODUCTION), Permission.HUMAN)
        self.assertEqual(decision.permission_for(PolicyAction.AUTO_MERGE), Permission.DENY)

    def test_fail_closed_blocks_privileged_actions(self) -> None:
        decision = fail_closed_decision("opa unavailable")

        self.assertEqual(decision.permission_for(PolicyAction.BLOCK), Permission.ALLOW)
        self.assertEqual(decision.permission_for(PolicyAction.AUTO_MERGE), Permission.DENY)
        self.assertEqual(decision.permission_for(PolicyAction.DEPLOY_STAGING), Permission.DENY)
        self.assertIn("opa unavailable", decision.blocked_reasons)


if __name__ == "__main__":
    unittest.main()

