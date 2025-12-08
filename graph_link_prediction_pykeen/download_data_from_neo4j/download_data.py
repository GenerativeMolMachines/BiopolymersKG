from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

db_api      = ""
db_login    = ""
db_password = ""


driver = GraphDatabase.driver(
    db_api,
    auth=(db_login, db_password)
)
driver.verify_connectivity()


QUERY_COUNT = """
    MATCH (e1)-[r]-(e2)
    RETURN count(DISTINCT apoc.rel.id(r)) AS total
"""

def get_total_rows():
    with driver.session() as session:
        return session.run(QUERY_COUNT).single()["total"]

def fetch_batch(query: str, last_rid: str, batch_size: int):
    """Возвращает список записей (batch)."""
    try:
        with driver.session() as session:
            records = session.run(
                query,
                last_rid=last_rid,
                batch=batch_size,
            )
            return list(records)
    except ServiceUnavailable as e:
        raise e

def close_driver():
    driver.close()
