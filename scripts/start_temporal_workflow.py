from __future__ import annotations

import asyncio
import os
from uuid import uuid4

from temporalio.client import Client

from control_plane.domain import SignalKind
from control_plane.workflows.temporal.workflows import WorkItemTemporalWorkflow


async def main() -> None:
    target = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    namespace = os.environ.get("TEMPORAL_NAMESPACE", "default")
    task_queue = os.environ.get("CONTROL_PLANE_TASK_QUEUE", "control-plane-v2")
    signal_id = str(uuid4())
    workflow_id = f"work-item-{signal_id}"
    client = await Client.connect(target, namespace=namespace)
    handle = await client.start_workflow(
        WorkItemTemporalWorkflow.run,
        {
            "id": signal_id,
            "kind": SignalKind.HUMAN_PROMPT.value,
            "summary": "Phase 1 Temporal durability proof",
            "payload": {},
            "source": "script",
        },
        id=workflow_id,
        task_queue=task_queue,
    )
    print({"workflow_id": workflow_id, "run_id": handle.result_run_id})
    print(await handle.result())


if __name__ == "__main__":
    asyncio.run(main())
