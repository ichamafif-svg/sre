from __future__ import annotations

import unittest

from control_plane.signals.ingest import alert
from control_plane.workflows.v2_workflow import V2Workflow, degraded_sample, healthy_sample
from control_plane.workitems.lifecycle import WorkItemState
from tests.fixtures.fixture_repo import healthy_repo, parser_bug_repo


class V2RemediationTest(unittest.TestCase):
    def test_alert_to_canary_then_human_required_for_production(self) -> None:
        signal = alert(
            "fixture parser alert: whitespace customer ids fail",
            {"service": "fixture-parser", "reason": "parser regression after recent release"},
        )

        outcome = V2Workflow().run_remediation(
            signal,
            parser_bug_repo(),
            canary_samples=(healthy_sample(), healthy_sample(), healthy_sample(), healthy_sample()),
        )

        self.assertEqual(outcome.item.state, WorkItemState.ESCALATED)
        self.assertTrue(outcome.production_human_required)
        self.assertIsNotNone(outcome.artifact)
        self.assertIn("raw.strip()", outcome.repo["service/parser.py"])
        self.assertTrue(outcome.item.pr_id)
        self.assertTrue(outcome.item.release_id)
        self.assertTrue(any("artifact:" in evidence for evidence in outcome.item.evidence))
        self.assertTrue(any("CANARY_OBSERVING->ESCALATED" in event for event in outcome.item.audit))

    def test_canary_degradation_rolls_back_to_previous_artifact(self) -> None:
        workflow = V2Workflow()
        baseline = workflow.builder.build(healthy_repo(), "baseline", "baseline-sbom")
        workflow.deployment.environments["production"].current_artifact = baseline

        signal = alert(
            "fixture parser alert: whitespace customer ids fail",
            {"service": "fixture-parser", "reason": "parser regression after recent release"},
        )
        outcome = workflow.run_remediation(
            signal,
            parser_bug_repo(),
            canary_samples=(healthy_sample(), degraded_sample()),
        )

        self.assertEqual(outcome.item.state, WorkItemState.ROLLED_BACK)
        self.assertTrue(outcome.rolled_back)
        self.assertEqual(workflow.deployment.environments["production"].current_artifact, baseline)
        self.assertTrue(any("canary unhealthy" in event for event in outcome.item.audit))


if __name__ == "__main__":
    unittest.main()

