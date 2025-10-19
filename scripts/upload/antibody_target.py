import os
import dotenv
import asyncio
from neo4j import GraphDatabase

dotenv.load_dotenv()


db_api = os.environ["NEO4J_URL"]
db_login = os.environ["NEO4J_URL"]
db_password = os.environ["NEO4J_URL"]

driver = GraphDatabase.driver(db_api, auth=(db_login, db_password))
driver.verify_connectivity()


async def upload_proteins():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///binding_db_proteins.csv' AS row
          CALL(row) {
              MERGE (n:protein {
                name: row.name,
                content: row.content,
                representation_type: row.representation_type,
                annotation: coalesce(row.annotation, '')
                })
          } IN TRANSACTIONS OF 500 ROWS
    """
    driver.execute_query(query)


async def upload_molecules():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///binding_db_molecules.csv' AS row
          CALL(row) {
              MERGE (n:small_moleule {
                name: row.name,
                content: row.content,
                representation_type: row.representation_type
                })
          } IN TRANSACTIONS OF 500 ROWS
    """
    driver.execute_query(query)


def upload_interactions():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///binding_db_protein_molecule_interaction.csv' AS row
          CALL(row) {
              MATCH (p:protein {name: row.protein_name, content: row.protein_name_content}),
              (s:small_molecule {name: row.small_molecule_name, row.small_molecule_content})
              MERGE (p)-[:interacts_with {kd: coalesce(row.kd, 'NaN')}]-(s)
          } IN TRANSACTIONS OF 500 ROWS
    """
    driver.execute_query(query)


async def main():
    tasks = [
        asyncio.create_task(upload_proteins()),
        asyncio.create_task(upload_molecules()),
    ]

    await asyncio.gather(*tasks)

    upload_interactions()


if __name__ == "__main__":
    asyncio.run(main())
