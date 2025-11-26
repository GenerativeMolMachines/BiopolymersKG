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
          LOAD CSV WITH HEADERS FROM 'file:///processed_binding_db/binding_db_proteins.csv' AS row
          CALL(row) {
              MERGE (n:protein {
                name: row.protein_name,
                content: row.protein_sequence
                })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)


async def upload_molecules():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///processed_binding_db/binding_db_molecules.csv' AS row
          CALL(row) {
              MERGE (n:small_molecule {
                name: row.molecule_name,
                content: row.molecule_smiles
                })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)


def upload_interactions():
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///processed_binding_db/binding_db_interactions_nodeids.csv' AS row
          CALL(row) {
              MATCH (p:protein) WHERE id(p) = toInteger(row.protein_nodeid)
              MATCH (p:small_molecule) WHERE id(s) = toInteger(row.molecule_nodeid)
              MERGE (p)-[:interacts_with {
                  kd: coalesce(row.kd, 'NaN'),
                  Ki_nM: coalesce(row.Ki_nM, 'NaN'),
                  IC50_nM: coalesce(row.IC50_nM, 'NaN'),
                  Kd_nM: coalesce(row.Kd_nM, 'NaN'),
                  EC50_nM: coalesce(row.EC50_nM, 'NaN'),
                  pH: coalesce(row.pH, 'NaN'),
                  Temp_C: coalesce(row.Temp_C, 'NaN')
              }]-(s)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)


async def main():
    # tasks = [
    #     asyncio.create_task(upload_proteins()),
    #     asyncio.create_task(upload_molecules()),
    # ]

    # await asyncio.gather(*tasks)

    upload_interactions()


if __name__ == "__main__":
    asyncio.run(main())
