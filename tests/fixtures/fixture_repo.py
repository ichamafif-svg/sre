from __future__ import annotations


def healthy_repo() -> dict[str, str]:
    return {
        "service/parser.py": (
            "def parse_customer_id(raw: str) -> int:\n"
            "    return int(raw.strip())\n"
        ),
        "service/app.py": (
            "from service.parser import parse_customer_id\n\n"
            "def handle(raw: str) -> dict:\n"
            "    return {'customer_id': parse_customer_id(raw)}\n"
        ),
        "tests/test_parser.py": (
            "from service.parser import parse_customer_id\n\n"
            "def test_parse_customer_id():\n"
            "    assert parse_customer_id('42') == 42\n"
        ),
    }


def parser_bug_repo() -> dict[str, str]:
    repo = healthy_repo()
    repo["service/parser.py"] = (
        "def parse_customer_id(raw: str) -> int:\n"
        "    return int(raw)\n"
    )
    return repo

