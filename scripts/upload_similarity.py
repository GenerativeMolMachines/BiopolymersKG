import os
import dotenv

import asyncio
from neo4j import GraphDatabase

dotenv.load_dotenv()

db = GraphDatabase.driver(
    uri=os.environ['NEO4J_URL'],
    auth=(os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'])
)


def upload_similarity_dna():
    print(f"uploading dna")

    query = """
    CALL apoc.periodic.iterate(
        "
        LOAD CSV WITH HEADERS FROM 'file:///similarity/dna_similarity_80.csv' as row
        return row
        ",
        "
        CALL {
            WITH row
            MATCH (n:dna {content: row.content_1}), (m:dna {content: row.content_2})
            MERGE (n)-[:has_similarity {score: row.similarity_score}]-(m)
        }
        ",
        { batchSize: 250, parallel: false }
    )
    """
    with db.session(database="neo4j") as session:

        result = session.run(query)
        print("dna result")
        print(result.values())

    print(f"uploaded dna")


def upload_similarity_rna():
    print(f"uploading rna")

    query = """
    CALL apoc.periodic.iterate(
        "
        LOAD CSV WITH HEADERS FROM 'file:///similarity/rna_similarity_80.csv' as row
        return row
        ",
        "
        CALL {
            WITH row
            MATCH (n:rna {content: row.content_1}), (m:rna {content: row.content_2})
            MERGE (n)-[:has_similarity {score: row.similarity_score}]-(m)
        }
        ",
        { batchSize: 250, parallel: false }
    )
    """
    with db.session(database="neo4j") as session:

        result = session.run(query)
        print("rna result")
        print(result.values())

    print(f"uploaded rna")


def upload_similarity_small_molecule():
    print(f"uploading smiles")

    query = """
    CALL apoc.periodic.iterate(
        "
        LOAD CSV WITH HEADERS FROM 'file:///similarity/smiles_similarity_80.csv' as row
        return row
        ",
        "
        CALL {
            WITH row
            MATCH (n:small_molecule {content: row.content_1}), (m:small_molecule {content: row.content_2})
            MERGE (n)-[:has_similarity {score: row.similarity_score}]-(m)
        }
        ",
        { batchSize: 250, parallel: false }
    )
    """
    with db.session(database="neo4j") as session:

        result = session.run(query)
        print("smiles result")
        print(result.values())

    print(f"uploaded smiles")


if __name__ == "__main__":
    upload_similarity_dna()
    # upload_similarity_rna()
    upload_similarity_small_molecule()
