from __future__ import annotations

import os

from control_plane.persistence.postgres import PostgresStore


def main() -> None:
    dsn = os.environ.get(
        "CONTROL_PLANE_DATABASE_URL",
        "postgresql://control_plane:control_plane@localhost:5432/control_plane",
    )
    PostgresStore(dsn).migrate()
    print("PostgreSQL migrations applied")


if __name__ == "__main__":
    main()

