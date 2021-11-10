from flask import Flask, Response
from flask_restful import Resource, Api, reqparse, abort
from uuid import UUID

from control_session.session import PresenterControlSession, ControlSessionAction, InvalidControlSessionActionException
from events.events import BackendDataUpdatedEvent, UtteranceEvent
from raspberry_client.client import RaspberryClient

app = Flask(__name__)
api = Api(app)

control_session_action_parser = reqparse.RequestParser()
control_session_action_parser.add_argument('action', required=True, type=ControlSessionAction,
                                           choices=list(ControlSessionAction))


def get_control_session_or_abort(control_session_uuid: UUID) -> PresenterControlSession:
    if control_session := app.iva.control_sessions.get(control_session_uuid, None):
        return control_session
    else:
        abort(404, message=f"Control session {str(control_session_uuid)} doesn't exist")


class ControlSessionResource(Resource):
    def post(self, session_uuid: UUID):
        control_session = get_control_session_or_abort(session_uuid)
        args = control_session_action_parser.parse_args()
        action = args['action']
        try:
            control_session.handle_action(action)
            return Response(status=204)
        except InvalidControlSessionActionException:
            abort(422, message='Invalid control action')

    def get(self, session_uuid: UUID):
        control_session = get_control_session_or_abort(session_uuid)
        return {
            'control_session': control_session.presenter_session.dict,
            'current_item': control_session.current_item
        }


class ControlSessionListResource(Resource):
    def get(self):
        sessions = []
        for session_uuid in app.iva.control_sessions:
            session = app.iva.control_sessions[session_uuid]
            sessions.append({
                'uuid': str(session_uuid),
                'type': session.presenter_session.session_type
            })
        return sessions


data_updated_type_parser = reqparse.RequestParser()
data_updated_type_parser.add_argument('data_type', required=True, type=BackendDataUpdatedEvent.DataType,
                                      choices=list(BackendDataUpdatedEvent.DataType))


class BackendDataUpdatedResource(Resource):
    def post(self):
        args = data_updated_type_parser.parse_args()
        data_type = args['data_type']
        data_updated_event = BackendDataUpdatedEvent(data_type)
        app.iva.event_scheduler.schedule_event(data_updated_event)
        return Response(status=204)


raspberry_action_parser = reqparse.RequestParser()
raspberry_action_parser.add_argument('action', required=True, type=RaspberryClient.Action,
                                     choices=list(RaspberryClient.Action))


class RaspberryClientResource(Resource):
    def post(self):
        args = raspberry_action_parser.parse_args()
        action = args['action']
        RaspberryClient.send_action_request(action)
        return Response(status=204)


utterance_parser = reqparse.RequestParser()
utterance_parser.add_argument('utterance', required=True, type=str)


class UtteranceResource(Resource):
    def post(self):
        args = utterance_parser.parse_args()
        utterance = args['utterance']
        utterance_event = UtteranceEvent(utterance)
        app.iva.event_scheduler.schedule_event(utterance_event)
        return Response(status=204)


api.add_resource(ControlSessionListResource, '/control-sessions/')
api.add_resource(ControlSessionResource, '/control-sessions/<uuid:session_uuid>/')
api.add_resource(BackendDataUpdatedResource, '/backend-data-updated/')
api.add_resource(RaspberryClientResource, '/invoke-raspberry-client-action/')
api.add_resource(UtteranceResource, '/utterance/')
