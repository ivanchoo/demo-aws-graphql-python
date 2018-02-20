# demo-aws-graphql

Sample GraphQL query:

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
