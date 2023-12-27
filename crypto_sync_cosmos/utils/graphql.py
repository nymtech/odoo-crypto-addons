from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


def graphql_request(url, query):
    client = Client(transport=AIOHTTPTransport(url=url), execute_timeout=30)
    query = gql(query)
    result = client.execute(query)
    return result
