from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
from uuid import UUID

from control_session.session import PresenterControlSession, ControllerAction, InvalidControlActionException

app = Flask(__name__)
api = Api(app)

control_session_action_parser = reqparse.RequestParser()
control_session_action_parser.add_argument('action', required=True, type=ControllerAction, choices=list(ControllerAction))


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
            return '', 200
        except InvalidControlActionException:
            abort(422, message='Invalid control action')

    def get(self, session_uuid: UUID):
        control_session = get_control_session_or_abort(session_uuid)
        return {
            'control_session': control_session.presenter_session.dict,
            'current_item': control_session.current_item
        }


class ControlSessionListResource(Resource):
    def get(self):
        return [str(session_uuid) for session_uuid in app.iva.control_sessions.keys()]


api.add_resource(ControlSessionListResource, '/control-sessions')
api.add_resource(ControlSessionResource, '/control-sessions/<uuid:session_uuid>')
