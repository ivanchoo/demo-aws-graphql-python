#!/usr/bin/env python
import sys
try:
    from flask import Flask  # noqa
except ImportError:
    sys.exit(
        'Failed to import dev dependencies. '
        'Did you run `pipenv install --dev --three`?'
    )


def main():
    app = Flask(__name__)
    app.debug = True

    from demo.schema import schema
    from flask_graphql import GraphQLView
    graphql_view = GraphQLView.as_view('graphql', schema=schema, graphiql=True)
    app.add_url_rule('/', view_func=graphql_view)

    app.run()


if __name__ == '__main__':
    main()
