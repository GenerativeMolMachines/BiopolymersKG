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
          LOAD CSV WITH HEADERS FROM 'file:///aptamer_datasets/aptamer.csv' AS row
          CALL(row) {
              MERGE (n:rna {
                name: row.name,
                content: row.content
                })
          } IN TRANSACTIONS OF 500 ROWS
    """
    with driver.session() as session:
        session.run(query)


async def upload_molecules():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///aptamer_datasets/small_molecule.csv' AS row
          CALL(row) {
              MERGE (n:small_molecule {
                name: row.name,
                content: row.content
                })
          } IN TRANSACTIONS OF 500 ROWS
    """
    with driver.session() as session:
        session.run(query)


def upload_interactions():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///aptamer_datasets/aptamers_annotation.csv' AS row
          CALL(row) {
              MATCH (r:rna {name: row.RNA_name, content: row.rna_content}),
              (s:small_molecule {name: row.small_molecule_name, content: row.small_molecule_content})
              MERGE (r)-[:interacts_with {kd: coalesce(row.kd, 'NaN')}]-(s)
          } IN TRANSACTIONS OF 500 ROWS
    """
    with driver.session() as session:
        session.run(query)


async def main():
    tasks = [
        asyncio.create_task(upload_rna()),
        asyncio.create_task(upload_molecules()),
    ]

    await asyncio.gather(*tasks)

    upload_interactions()


if __name__ == "__main__":
    asyncio.run(main())
