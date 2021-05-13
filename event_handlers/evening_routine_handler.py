from event_handlers.routine_handler import RoutineEventHandler
from websocket.message import WebSocketMessageAction


class EveningRoutineEventHandler(RoutineEventHandler):
    async def handle(self):
        start_routine_data = {
            'routine_name': 'evening_routine'
        }
        await self.send_routine_message(WebSocketMessageAction.START_ROUTINE, start_routine_data)
        self.wait_for_confirmation()

        for step in range(3):
            await self.send_routine_message(WebSocketMessageAction.NEXT_STEP_IN_ROUTINE, {})
            self.wait_for_confirmation()

        await self.send_routine_message(WebSocketMessageAction.FINISH_ROUTINE, {})
