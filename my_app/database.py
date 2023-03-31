import psycopg2

def get_conn():
    conn = psycopg2.connect(
        'postgres://LuigiP99:nDojB7gIS2qX@ep-hidden-snowflake-082754.us-west-2.aws.neon.tech/neondb'
        )
    
    return conn
