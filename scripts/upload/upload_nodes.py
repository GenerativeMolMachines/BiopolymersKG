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


async def upload_aa():
    """Загрузка аминокислотных последовательностей из AA.csv"""
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes/AA.csv' AS row
    CALL(row) {
        MERGE (n:aa {node_id: toInteger(row.id)})
        SET n.content = row.content,
            n.name = row.name,
            n.alias = coalesce(row.alias, ''),
            n.source = row.source
    } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ AA загружены")


async def upload_dna():
    """Загрузка DNA последовательностей из DNA.csv"""
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes/DNA.csv' AS row
    CALL(row) {
        MERGE (n:dna {node_id: toInteger(row.id)})
        SET n.content = row.content,
            n.name = row.name,
            n.alias = coalesce(row.alias, ''),
            n.source = row.source
    } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ DNA загружены")


async def upload_rna():
    """Загрузка RNA последовательностей из RNA.csv"""
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes/RNA.csv' AS row
    CALL(row) {
        MERGE (n:rna {node_id: toInteger(row.id)})
        SET n.content = row.content,
            n.name = row.name,
            n.alias = coalesce(row.alias, ''),
            n.source = row.source
    } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ RNA загружены")


async def upload_small_molecules():
    """Загрузка малых молекул (SMILES) из SmallMolecule.csv"""
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes/SmallMolecule.csv' AS row
    CALL(row) {
        MERGE (n:small_molecule {node_id: toInteger(row.id)})
        SET n.content = row.content,
            n.name = row.name,
            n.alias = coalesce(row.alias, ''),
            n.source = row.source
    } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ SmallMolecule загружены")


async def upload_nucleic_ambiguous():
    """Загрузка неоднозначных нуклеиновых последовательностей из NucleicAmbigous.csv"""
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes/NucleicAmbigous.csv' AS row
    CALL(row) {
        MERGE (n:nucleic_ambiguous {node_id: toInteger(row.id)})
        SET n.content = row.content,
            n.name = row.name,
            n.alias = coalesce(row.alias, ''),
            n.source = row.source
    } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ NucleicAmbigous загружены")


async def upload_nucleic_mixed():
    """Загрузка смешанных (RNA/DNA) нуклеиновых последовательностей из NucleicMixed.csv"""
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes/NucleicMixed.csv' AS row
    CALL(row) {
        MERGE (n:nucleic_mixed {node_id: toInteger(row.id)})
        SET n.content = row.content,
            n.name = row.name,
            n.alias = coalesce(row.alias, ''),
            n.source = row.source
    } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ NucleicMixed загружены")


async def main():
    print("=" * 60)
    print("Загрузка узлов в Neo4j")
    print("=" * 60)

    # Параллельная загрузка всех типов узлов
    tasks = [
        asyncio.create_task(upload_aa()),
        asyncio.create_task(upload_dna()),
        asyncio.create_task(upload_rna()),
        asyncio.create_task(upload_small_molecules()),
        asyncio.create_task(upload_nucleic_ambiguous()),
        asyncio.create_task(upload_nucleic_mixed()),
    ]
    await asyncio.gather(*tasks)

    print("\n" + "=" * 60)
    print("Загрузка завершена!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
