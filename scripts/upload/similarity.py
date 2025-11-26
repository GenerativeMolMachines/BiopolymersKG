import os
import warnings
import dotenv
import asyncio
from neo4j import GraphDatabase

dotenv.load_dotenv()

warnings.filterwarnings("ignore")


db_api = os.environ["NEO4J_URL"]
db_login = os.environ["NEO4J_USER"]
db_password = os.environ["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(db_api, auth=(db_login, db_password))
driver.verify_connectivity()


async def upload_rna_similarity():
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///db_similarity/rna_similarity.csv' AS row
          CALL(row) {
              MATCH (r1:rna) WHERE id(r1) = toInteger(row.nodeid_1)
              MATCH (r2:rna) WHERE id(r2) = toInteger(row.nodeid_2)
              MERGE (r1)-[:has_similarity {score: row.score}]-(r2)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)

    print("loaded rna similarity")


async def upload_dna_similarity():
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///db_similarity/dna_similarity.csv' AS row
          CALL(row) {
              MATCH (r1:dna) WHERE id(r1) = toInteger(row.nodeid_1)
              MATCH (r2:dna) WHERE id(r2) = toInteger(row.nodeid_2)
              MERGE (r1)-[:has_similarity {score: row.score}]-(r2)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)

    print("loaded dna similarity")


async def upload_small_molecules_similarity():
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///db_similarity/small_molecule_similarity.csv' AS row
          CALL(row) {
              MATCH (r1:small_molecule) WHERE id(r1) = toInteger(row.nodeid_1)
              MATCH (r2:small_molecule) WHERE id(r2) = toInteger(row.nodeid_2)
              MERGE (r1)-[:has_similarity {tanimoto: row.score}]-(r2)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)

    print("loaded small molecules similarity")


async def main():
    tasks = [
        asyncio.create_task(upload_rna_similarity()),
        asyncio.create_task(upload_dna_similarity()),
        asyncio.create_task(upload_small_molecules_similarity()),
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
