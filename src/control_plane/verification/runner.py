from __future__ import annotations

import hashlib
from dataclasses import dataclass

from control_plane.agents.backend import Patch


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    reproduction_passed: bool
    regression_test_added: bool
    targeted_tests_passed: bool
    architecture_checks_passed: bool
    security_checks_passed: bool
    sbom_hash: str
    command_log: tuple[str, ...]
    output_ref: str


def apply_patch(repo: dict[str, str], patch: Patch) -> dict[str, str]:
    updated = dict(repo)
    updated.update(patch.changed_files)
    updated.update(patch.tests_added)
    return updated


def _parser_accepts_whitespace(repo: dict[str, str]) -> bool:
    parser = repo.get("service/parser.py", "")
    return "raw.strip()" in parser


class VerificationRunner:
    def verify(self, before: dict[str, str], patch: Patch, changed_paths: tuple[str, ...]) -> VerificationResult:
        after = apply_patch(before, patch)
        reproduction_passed = patch.reproduction_before_patch and not _parser_accepts_whitespace(before)
        regression_test_added = any("regression" in path for path in patch.tests_added)
        targeted_tests_passed = _parser_accepts_whitespace(after)
        architecture_checks_passed = not any(path.startswith("policy/") for path in changed_paths)
        security_checks_passed = not any("SECRET=" in content for content in after.values())
        sbom_material = "\n".join(f"{path}:{hashlib.sha256(content.encode()).hexdigest()}" for path, content in sorted(after.items()))
        sbom_hash = hashlib.sha256(sbom_material.encode()).hexdigest()
        passed = all(
            (
                reproduction_passed,
                regression_test_added,
                targeted_tests_passed,
                architecture_checks_passed,
                security_checks_passed,
            )
        )
        return VerificationResult(
            passed=passed,
            reproduction_passed=reproduction_passed,
            regression_test_added=regression_test_added,
            targeted_tests_passed=targeted_tests_passed,
            architecture_checks_passed=architecture_checks_passed,
            security_checks_passed=security_checks_passed,
            sbom_hash=sbom_hash,
            command_log=(
                "fixture: reproduce parser whitespace failure",
                "fixture: run regression tests",
                "fixture: architecture changed-path checks",
                "fixture: security scan for embedded secrets",
                "fixture: generate SBOM hash",
            ),
            output_ref=f"evidence://verification/{sbom_hash}",
        )

