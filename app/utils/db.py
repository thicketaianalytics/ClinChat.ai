import psycopg2
import logging
from psycopg2 import pool

db_config = {
    "host": "aact-db.ctti-clinicaltrials.org",
    "port": 5432,
    "database": "aact",
    "user": "srinidreambig",
    "password": "SRmadhu@143",
}
connection_pool = None


def initialize_connection_pool():
    """Initializes the PostgreSQL connection pool."""
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = pool.SimpleConnectionPool(
                minconn=2, maxconn=10, **db_config
            )
            logging.info("Database connection pool initialized.")
        except Exception as e:
            logging.exception(f"Failed to initialize database connection pool: {e}")


def get_db_connection():
    """Gets a connection from the pool."""
    if connection_pool is None:
        initialize_connection_pool()
    if connection_pool:
        try:
            return connection_pool.getconn()
        except Exception as e:
            logging.exception(f"Failed to get connection from pool: {e}")
    return None


def return_db_connection(conn):
    """Returns a connection to the pool."""
    if connection_pool and conn:
        try:
            connection_pool.putconn(conn)
        except Exception as e:
            logging.exception(f"Failed to return connection to pool: {e}")


def close_connection_pool():
    """Closes all connections in the pool."""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        connection_pool = None
        logging.info("Database connection pool closed.")