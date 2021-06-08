import uuid

from event_handlers.routine_handler import RoutineEventHandler
from events.events import MindfulSessionRecordedEvent
from websocket.message import WebSocketMessageAction


class MorningRoutineEventHandler(RoutineEventHandler):
    async def handle(self):
        await self.turn_screen_on()

        start_routine_data = {
            'routine_name': 'morning_routine'
        }

        await self.send_routine_message(WebSocketMessageAction.START_ROUTINE, start_routine_data)
        self.wait_for_event_uuid(uuid.uuid4())

        for step in range(4):
            await self.send_routine_message(WebSocketMessageAction.NEXT_STEP_IN_ROUTINE, {})
            # Mindful step can be automatically confirmed by receiving data about a mindful session
            # or it can be confirmed by uuid
            if step == 1:
                self.wait_for_event_uuid_or_type(uuid.uuid4(), MindfulSessionRecordedEvent)
            else:
                self.wait_for_event_uuid(uuid.uuid4())

        await self.send_routine_message(WebSocketMessageAction.FINISH_ROUTINE, {})
