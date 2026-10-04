from __future__ import annotations

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from control_plane.workflows.temporal.activities import (
    advance_state_activity,
    evaluate_policy_activity,
    normalize_signal_activity,
    reserve_external_mutation_activity,
)
from control_plane.workflows.temporal.workflows import WorkItemTemporalWorkflow


async def main() -> None:
    target = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    namespace = os.environ.get("TEMPORAL_NAMESPACE", "default")
    task_queue = os.environ.get("CONTROL_PLANE_TASK_QUEUE", "control-plane-v2")
    client = await Client.connect(target, namespace=namespace)
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[WorkItemTemporalWorkflow],
        activities=[
            normalize_signal_activity,
            evaluate_policy_activity,
            reserve_external_mutation_activity,
            advance_state_activity,
        ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
