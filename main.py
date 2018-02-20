# Activate virtual environment in sam-local lambda runtime
# this is required only for development
import os
CWD = os.path.abspath(os.path.dirname(__file__))  # noqa
VENV_ACTIVATE = os.path.join(CWD, '.venv', 'bin', 'activate_this.py') # noqa
if os.path.isfile(VENV_ACTIVATE): # noqa
    exec(open(VENV_ACTIVATE).read(), dict(__file__=VENV_ACTIVATE)) # noqa

from demo.schema import schema
from graphql_lambda import create_response

GQL_ENABLE_BATCH = bool(os.environ.get('GQL_ENABLE_BATCH', '1'))
GQL_ENABLE_GRAPHIQL = bool(os.environ.get('GQL_ENABLE_GRAPHIQL', '1'))


def graphql_handler(event, context):
    try:
        return create_response(
            event, context,
            schema=schema,
            enable_batch=GQL_ENABLE_BATCH,
            enable_graphiql=GQL_ENABLE_GRAPHIQL
        )
    except Exception as e:
        print(e)
        raise e
