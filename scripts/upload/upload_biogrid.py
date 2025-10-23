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


async def upload_proteins():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///processed_biogrid/protein_data_biogrid.csv' AS row
          CALL(row) {
              MERGE (n:protein {
                name: row.protein_name,
                content: row.protein_sequence
                })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)


def upload_interactions():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///processed_biogrid/biogrid_ppi_unique.csv' AS row
          CALL(row) {
              MATCH (p1:protein {name: row.protein_name_a, content: row.protein_sequence_a}),
              (p2:protein {name: row.protein_name_b, content: row.protein_sequence_b})
              MERGE (p1)-[:interacts_with]-(p2)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)


async def main():
    tasks = [
        asyncio.create_task(upload_proteins()),
    ]

    await asyncio.gather(*tasks)

    upload_interactions()


if __name__ == "__main__":
    asyncio.run(main())
