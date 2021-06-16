import os

_conn = {
    'USERNAME': 'user_name',
    'PASSWORD': 'password',
    'ACCOUNT': 'account',
    'WAREHOUSE': 'warehouse'
}
_conn.update(dict(os.environ))

local_secrets = {
    # Neo4j should be a different "secret" in prod but reusing it here for local testing
    # since the top-level key does not conflict
    'NEO4J_USERNAME': 'neo4j',
    'NEO4J_PASSWORD': 'test',
    'TYPE': 'snowflake',
    # Make sure you have the connection details in your environment variables
    'CONNECTION': _conn,
    'DATABASES': [
        {
            "METADATA": True,
            "NAME": "\"ca_covid\"",
            "STATS": True
        },
        {
            "METADATA": True,
            "NAME": "SNOWFLAKE_SAMPLE_DATA",
            "STATS": True
        }
    ]
}
