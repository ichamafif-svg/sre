from __future__ import annotations

import unittest

from control_plane.idempotency import stable_idempotency_key


class IdempotencyTest(unittest.TestCase):
    def test_stable_idempotency_key_ignores_retry_attempts(self) -> None:
        first = stable_idempotency_key("work-item-1", "OPEN_PR")
        second = stable_idempotency_key("work-item-1", "OPEN_PR")
        different_operation = stable_idempotency_key("work-item-1", "DEPLOY_STAGING")

        self.assertEqual(first, second)
        self.assertNotEqual(first, different_operation)


if __name__ == "__main__":
    unittest.main()
