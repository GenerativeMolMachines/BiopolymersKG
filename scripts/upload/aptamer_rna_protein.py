import os
import dotenv
import asyncio
from neo4j import GraphDatabase

dotenv.load_dotenv()


db_api = os.environ["NEO4J_URL"]
db_login = os.environ["NEO4J_USER"]
db_password = os.environ["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(db_api, auth=(db_login, db_password))
driver.verify_connectivity()


async def upload_rna():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///new_aptamers_rna_protein/dna.csv' AS row
          CALL(row) {
              MERGE (n:rna {
                name: row.name,
                content: row.content
                })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)


async def upload_protein():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///new_aptamers_rna_protein/protein.csv' AS row
          CALL(row) {
              MERGE (n:protein {
                name: row.name,
                content: row.content
                })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)


def upload_interactions():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///new_aptamers_rna_protein/new_aptamers_interactions.csv' AS row
          CALL(row) {
              MATCH (d:rna {name: row.apt_name, content: row.apt_seq}),
              (s:protein {name: row.target_name, content: row.target_seq})
              MERGE (d)-[:interacts_with]-(s)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)


async def main():
    tasks = [
        asyncio.create_task(upload_rna()),
        asyncio.create_task(upload_protein()),
    ]

    await asyncio.gather(*tasks)

    upload_interactions()


if __name__ == "__main__":
    asyncio.run(main())
