from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_PATHS = {
    ".tools/Postgres.app/Contents/Versions/16/bin/postgres": "PostgreSQL server",
    ".tools/Postgres.app/Contents/Versions/16/bin/psql": "PostgreSQL client",
    ".tools/bin/temporal": "Temporal CLI and development server",
    ".tools/bin/opa": "OPA policy runtime",
    ".venv/bin/python": "Project Python runtime with phase1 dependencies",
}


def command_result(command: list[str]) -> dict:
    try:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=10, check=False)
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except FileNotFoundError as exc:
        return {"command": command, "returncode": 127, "stdout": "", "stderr": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "returncode": 124, "stdout": exc.stdout or "", "stderr": exc.stderr or "timeout"}


def main() -> int:
    report: dict = {
        "gate": "A",
        "status": "PENDING",
        "binary_checks": {},
        "compose_file": "deploy/phase1/docker-compose.yml",
        "commands": [],
        "missing": [],
    }

    for binary, purpose in REQUIRED_PATHS.items():
        path = Path(binary)
        report["binary_checks"][binary] = {"path": str(path), "purpose": purpose, "exists": path.exists()}
        if not path.exists():
            report["missing"].append(binary)

    compose = Path("deploy/phase1/docker-compose.yml")
    if not compose.exists():
        report["missing"].append(str(compose))

    if report["missing"]:
        report["status"] = "BLOCKED"
        report["reason"] = "Required runtime dependencies are unavailable; Gate A cannot be proven live."
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    report["commands"].append(command_result([".tools/Postgres.app/Contents/Versions/16/bin/postgres", "--version"]))
    report["commands"].append(command_result([".tools/bin/temporal", "--version"]))
    report["commands"].append(command_result([".tools/bin/opa", "version"]))

    if any(item["returncode"] != 0 for item in report["commands"]):
        report["status"] = "BLOCKED"
        report["reason"] = "Runtime commands are present but failed prerequisite checks."
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    report["status"] = "READY_TO_RUN"
    report["next_commands"] = [
        "LC_ALL=C LANG=C .tools/Postgres.app/Contents/Versions/16/bin/pg_ctl -D .tools/pgdata -l .tools/postgres.log -o \"-p 5432\" start -w",
        ".tools/bin/opa run --server --addr localhost:8181 policy/rego",
        ".tools/bin/temporal server start-dev --ip 127.0.0.1 --port 7233 --ui-port 8233 --db-filename .tools/temporal-dev.db",
        "CONTROL_PLANE_DATABASE_URL=postgresql://control_plane:control_plane@localhost:5432/control_plane python scripts/migrate_postgres.py",
        "CONTROL_PLANE_DATABASE_URL=postgresql://control_plane:control_plane@localhost:5432/control_plane python scripts/run_temporal_worker.py",
        "CONTROL_PLANE_DATABASE_URL=postgresql://control_plane:control_plane@localhost:5432/control_plane python scripts/start_temporal_workflow.py",
    ]
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
