from flask import Flask, abort
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import sys
from datetime import datetime, date

app = Flask(__name__)

# write your code here
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()
api = Api(app)
parser = reqparse.RequestParser()
parser2 = reqparse.RequestParser()


class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime('%Y-%m-%d')


model = {
    'id': fields.Integer,
    'event': fields.String,
    'date': MyDateFormat
}


class TodayEvents(Resource):
    @marshal_with(model)
    def get(self):
        event = Event.query.filter(Event.date == date.today()).all()
        print(event[0].id)
        print(event[0].event)
        print(type(event[0].date))
        return event



parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)
parser.add_argument(
    'date',
    type=inputs.date,
    help='The event date with the correct format is required! The correct format is YYYY-MM-DD!',
    required=True
)


class AddEvent(Resource):
    def post(self):
        args = parser.parse_args()
        # print(type(args['date']))
        event = Event(event=args['event'], date=args['date'])
        db.session.add(event)
        db.session.commit()
        return {
                "message": "The event has been added!",
                "event": args['event'],
                "date": args['date'].strftime("%Y-%m-%d")
                }


class GetEventById(Resource):
    @marshal_with(model)
    def get(self, event_id):
        print('getting by id', event_id)
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        print("event by id:", event)
        return event


class DeleteEventById(Resource):
    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event:
            db.session.delete(event)
            db.session.commit()
            return {
                "message": "The event has been deleted!"
            }
        else:
            abort(404, "The event doesn't exist!")


parser2.add_argument(
    'start_time',
    type=inputs.date
)

parser2.add_argument(
    'end_time',
    type=inputs.date
)


class GetEventsByDates(Resource):
    @marshal_with(model)
    def get(self):
        args = parser2.parse_args()
        if args['start_time'] and args['end_time']:
            print('dates', args['start_time'], args['end_time'])
            events = Event.query.filter(Event.date >= args['start_time']).filter(Event.date <= args['end_time']).limit(1).all()
            print(events)
        else:
            print('Get:')
            events = Event.query.all()
            print(events[0].date)
        return events


api.add_resource(HelloWorldResource, '/hello')
api.add_resource(TodayEvents, '/event/today')
api.add_resource(AddEvent, '/event')
# api.add_resource(AllEvent, '/event')
api.add_resource(GetEventById, '/event/<int:event_id>')
api.add_resource(DeleteEventById, '/event/<int:event_id>')
api.add_resource(GetEventsByDates, '/event')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
