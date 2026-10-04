from __future__ import annotations

import unittest

from control_plane.domain import Permission, PolicyAction, ScopeGrant
from control_plane.policy.engine import LocalPolicyEngine
from control_plane.risk.model import assess_risk
from control_plane.signals.ingest import human_prompt


class PolicyTest(unittest.TestCase):
    def test_low_risk_verified_allows_auto_merge_but_not_auto_prod(self) -> None:
        risk = assess_risk(human_prompt("narrow parser fix"))
        scope = ScopeGrant(("service/parser.py", "tests"), ("policy/",), ("python-test",), (), ("sandbox",), "fixture")
        decision = LocalPolicyEngine().decide(risk, scope, verification_passed=True)

        self.assertEqual(decision.permission_for(PolicyAction.AUTO_MERGE), Permission.ALLOW)
        self.assertEqual(decision.permission_for(PolicyAction.DEPLOY_PRODUCTION), Permission.HUMAN)


if __name__ == "__main__":
    unittest.main()
