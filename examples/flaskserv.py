import flask
from flask import request
from happyly.serialization import DummyValidator

import happyly
import marshmallow

from serialization.flask import JsonifyForSchema

app = flask.Flask(__name__)


class MyInputSchema(happyly.Schema):
    request_id = marshmallow.fields.Str(required=True)


class MyOutputSchema(happyly.Schema):
    request_id = marshmallow.fields.Str(required=True)
    result = marshmallow.fields.Str(required=True)
    error = marshmallow.fields.Str()


def handle_things(message):
    print(message)
    return {'request_id': '1', 'result': '2'}


@app.route('/', methods=['POST'])
def root():
    executor = happyly.Executor(
        handler=handle_things,
        deserializer=DummyValidator(schema=MyInputSchema()),
        serializer=JsonifyForSchema(schema=MyOutputSchema()),
    )
    request_data = request.get_json()
    return executor.run_for_result(request_data)


app.run()
