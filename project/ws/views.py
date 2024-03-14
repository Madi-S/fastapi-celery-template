import json
from fastapi import WebSocket

from project import broadcast
from project.ws import ws_router
from project.celery_utils import get_task_info


@ws_router.websocket('/ws/task_status/{task_id}')
async def ws_task_status(websocket: WebSocket):
    await websocket.accept()

    task_id = websocket.scope['path_params']['task_id']

    async with broadcast.subscribe(channel=task_id) as subscriber:
        data = get_task_info(task_id)
        await websocket.send(data)

        async for event in subscriber:
            response = json.loads(event.message)
            await websocket.send_json(response)


async def update_celery_task_status(task_id: str):
    await broadcast.connect()
    await broadcast.publish(
        channel=task_id,
        message=json.dumps(get_task_info(task_id))
    )
    await broadcast.disconnect()
