import urllib.parse

from graphql_server import (default_format_error, encode_execution_results,
                            json_encode, load_json_body, run_http_query)

GRAPHIQL_VERSION = '0.7.1'


def create_response(
        event, context,
        schema=None, enable_batch=False, enable_graphiql=False):
    """Creates an API-Gateway response object for a graphql request."""
    # This is shamelessly adapted from
    # https://github.com/graphql-python/flask-graphql/blob/master/flask_graphql/graphqlview.py
    assert event, 'Expects event, got `{}`'.format(event)
    assert schema, 'Expects schema, got `{}`'.format(schema)
    request_method = event.get('httpMethod', 'get').lower()
    # sam-local header keys are inconsistently mixed-cased, so we lower-case em
    headers = dict(
        (k.lower(), v) for k, v in event.get('headers', {}).items()
    )
    body = event.get('body', '')
    query_data = event.get('queryStringParameters', {})
    content_type = headers.get('content-type')
    if content_type == 'application/graphql':
        data = {'query': body}
    elif content_type == 'application/json':
        data = load_json_body(body)
    elif content_type in (
            'application/x-www-form-urlencoded', 'multipart/form-data'):
        data = urllib.parse.parse_qs(body)
    else:
        data = {}
    wants_graphiql = request_method == 'get'
    catch_http_errors = wants_graphiql
    execution_results, all_params = run_http_query(
        schema,
        request_method,
        data,
        query_data=query_data,
        batch_enabled=enable_batch,
        catch=catch_http_errors,
        # Execute options
        root_value=None,        # TODO: enabling root value
        context_value=context,
        middleware=None,        # TODO: consider middleware support
        executor=None,          # TODO: consider executor
    )
    result, status_code = encode_execution_results(
        execution_results,
        is_batch=isinstance(data, list),
        format_error=default_format_error,
        encode=json_encode
    )
    if wants_graphiql and enable_graphiql:
        return {
            'statusCode': 200,
            'body': TEMPLATE,
            'headers': {
                'content-type': 'text/html'
            }
        }
    # Else always render json response
    return {
        'statusCode': status_code,
        'body': result,
        'headers': {
            'content-type': 'application/json'
        }
    }


def render_graphiql(params, result, graphiql_version=GRAPHIQL_VERSION):
    pass

# See https://github.com/graphql-python/flask-graphql/blob/master/flask_graphql/render_graphiql.py  # noqa


TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
  <title>GraphQL + API-Gateway + Lambda</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      width: 100%;
    }
  </style>
  <meta name="referrer" content="no-referrer">
  <link href="//cdn.jsdelivr.net/graphiql/{graphiql_version}/graphiql.css" rel="stylesheet" />
  <script src="//cdn.jsdelivr.net/fetch/0.9.0/fetch.min.js"></script>
  <script src="//cdn.jsdelivr.net/react/15.0.0/react.min.js"></script>
  <script src="//cdn.jsdelivr.net/react/15.0.0/react-dom.min.js"></script>
  <script src="//cdn.jsdelivr.net/graphiql/{graphiql_version}/graphiql.min.js"></script>
</head>
<body>
  <script>
    // Collect the URL parameters
    var parameters = {};
    window.location.search.substr(1).split('&').forEach(function (entry) {
      var eq = entry.indexOf('=');
      if (eq >= 0) {
        parameters[decodeURIComponent(entry.slice(0, eq))] =
          decodeURIComponent(entry.slice(eq + 1));
      }
    });
    // Produce a Location query string from a parameter object.
    function locationQuery(params) {
      return '?' + Object.keys(params).map(function (key) {
        return encodeURIComponent(key) + '=' +
          encodeURIComponent(params[key]);
      }).join('&');
    }
    // Derive a fetch URL from the current URL, sans the GraphQL parameters.
    var graphqlParamNames = {
      query: true,
      variables: true,
      operationName: true
    };
    var otherParams = {};
    for (var k in parameters) {
      if (parameters.hasOwnProperty(k) && graphqlParamNames[k] !== true) {
        otherParams[k] = parameters[k];
      }
    }
    var fetchURL = locationQuery(otherParams);
    // Defines a GraphQL fetcher using the fetch API.
    function graphQLFetcher(graphQLParams) {
      return fetch(fetchURL, {
        method: 'post',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(graphQLParams),
        credentials: 'include',
      }).then(function (response) {
        return response.text();
      }).then(function (responseBody) {
        try {
          return JSON.parse(responseBody);
        } catch (error) {
          return responseBody;
        }
      });
    }
    // When the query and variables string is edited, update the URL bar so
    // that it can be easily shared.
    function onEditQuery(newQuery) {
      parameters.query = newQuery;
      updateURL();
    }
    function onEditVariables(newVariables) {
      parameters.variables = newVariables;
      updateURL();
    }
    function onEditOperationName(newOperationName) {
      parameters.operationName = newOperationName;
      updateURL();
    }
    function updateURL() {
      history.replaceState(null, null, locationQuery(parameters));
    }
    // Render <GraphiQL /> into the body.
    ReactDOM.render(
      React.createElement(GraphiQL, {
        fetcher: graphQLFetcher,
        onEditQuery: onEditQuery,
        onEditVariables: onEditVariables,
        onEditOperationName: onEditOperationName,
        query: null,
        response: null,
        variables: null,
        operationName: null,
      }),
      document.body
    );
  </script>
</body>
</html>'''  # noqa

TEMPLATE = TEMPLATE.replace('{graphiql_version}', GRAPHIQL_VERSION)
