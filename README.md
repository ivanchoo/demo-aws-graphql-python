# Python powered GraphQL in AWS Lambda

This project is a proof of concept to run the [Graphene](http://graphene-python.org) implementation of GraphQL in AWS Lambda.

 - Serverless GraphQL (API-Gateway + Lambda)
 - Uses Graphene-Python implementation
 - Datastore agnostic: Use [Graphene-SQLAlchemy](http://docs.graphene-python.org/projects/sqlalchemy/en/latest/) for AWS RDS, or custom resolvers for other AWS resources

## Local development setup

Install [pipenv](https://github.com/pypa/pipenv)

```
$ pip install pipenv
```

Install dependencies

```
$ export PIPENV_VENV_IN_PROJECT=true
$ pipenv install --dev --three
```

**Note: We are using the python3.6 lambda execution environment in AWS. Please make sure you're using the same python version during development.**

## Local Flask development server

To run a local Flask server for development:

```
pipenv run ./cli.py server
```

Although we're building serverless applications, I generally find it useful to run a local flask server that quickly mocks out API endpoints to serve mock data. This allows us to develop offline and not wrestle with serverless tools, while keeping mock data out of the frontend codebase.

This demo serves GraphQL queries from an in-memory data storage, together with GraphiQL UI interface for testing queries. Test drive the following query in the local flask server [http://127.0.0.1:5000/]:

```
{
  user {
    id
    userId
    firstName
    lastName
    email
    avatarUrl
    education
    job
    address
    introduction
    friends {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          userId
          firstName
          lastName
          friends {
            edges {
              node {
                id
                userId
                firstName
                lastName
              }
            }
          }
        }
      }
    }
  }
}
```

## Testing out API-Gateway locally

To test API-Gateway locally, you'll need to install [AWS SAM Local](https://github.com/awslabs/aws-sam-local).

```
$ sam local start-api
```

This will serve the Lambda function over a local web server [http://127.0.0.1:3000]

## Deploying the serverless application

Remove development dependencies before we build the project.

```
$ pipenv --rm
```

Install only runtime dependencies.

```
$ pipenv install --three
```

Run the build command. This will create the package in `build` folder.

```
$ pipenv run ./cli.py build
```

Run CloudFormation command to send the package to an S3 bucket. Be sure to have the [AWS CLI tools](https://github.com/aws/aws-cli) & credentials installed. This will generate a `template.deploy.yml` which we will deploy with using CloudFormation.

```
$ aws cloudformation package \
  --template-file template.yml \
  --s3-bucket you-s3-bucket \
  --output-template-file template.deploy.yml
```

Run CloudFormation deployment.

```
$ aws cloudformation deploy \
  --template-file template.deploy.yml \
  --parameter-overrides EnvironmentName=my-graphql \
  --capabilities CAPABILITY_IAM \
  --stack-name my-graphql
```

## Cleaning up

Remove local build stuff.

```
$ pipenv run ./cli.py clean
```

Remove python virtual environment.

```
$ pipenv --rm
```

You can remove the CloudFormation stack in the [AWS Console](http://console.aws.amazon.com)
