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


async def upload_rna_similarity():
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///similarity_new/rna_similarity.csv' AS row
          CALL(row) {
              MATCH (r1:rna {name: row.name_1, content: row.sequence_1}),
              (r2:rna {name: row.name_2, content: row.sequence_2}),
              MERGE (r1)-[:has_similarity {score: row.score}]-(r2)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)

    print("loaded rna similarity")


async def upload_dna_similarity():
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///similarity_new/dna_similarity.csv' AS row
          CALL(row) {
              MATCH (r1:dna {name: row.name_1, content: row.sequence_1}),
              (r2:dna {name: row.name_2, content: row.sequence_2}),
              MERGE (r1)-[:has_similarity {score: row.score}]-(r2)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)

    print("loaded dna similarity")


async def upload_small_molecules_similarity():
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///similarity_new/small_molecule_similarity.csv' AS row
          CALL(row) {
              MATCH (r1:small_molecule {name: row.name_1, content: row.sequence_1}),
              (r2:small_molecule {name: row.name_2, content: row.sequence_2}),
              MERGE (r1)-[:has_similarity {tanimoto: row.tanimoto}]-(r2)
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
