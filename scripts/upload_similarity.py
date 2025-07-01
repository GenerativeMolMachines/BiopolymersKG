import os
import dotenv

import asyncio
from neo4j import GraphDatabase

dotenv.load_dotenv()

db = GraphDatabase.driver(
    uri=os.environ['NEO4J_URL'],
    auth=(os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'])
)


async def upload_similarity(label: str, filename: str):
    print(f"uploading {label}")

    query_pattern = """
    CALL apoc.periodic.iterate(
        "
        LOAD CSV WITH HEADERS 'file:///{filename}' as row
        return row
        ",
        "
        CALL {
            WITH row
            MATCH (n:{label} {content: row.content_1}), (m:{label} {content: row.content_2})
            MERGE (n)-[:has_similarity {score: row.similarity_score}]-(m)
        }
        ",
        { batchSize: 250, parallel: true }
    )
    """
    with db.session(database="neo4j") as session:
        query = query_pattern.format(filename=filename, label=label)
        session.run(query)

    print(f"uploaded {label}")


async def main():
    await upload_similarity(label="dna", filename="similarity/dna_similarity_80.csv")
    await upload_similarity(label="rna", filename="similarity/rna_similarity_80.csv")
    await upload_similarity(label="small_molecule", filename="similarity/smiles_similarity_80.csv")


if __name__ == "__main__":
    asyncio.run(main())
