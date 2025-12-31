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


async def upload_dna_aptamers():
    """Загрузка DNA аптамеров из aptabench_dna_final.csv"""
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///aptabench_dna_final.csv' AS row
          CALL(row) {
              MERGE (n:dna {
                name: row.name,
                content: row.content
                })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ DNA аптамеры загружены")


async def upload_rna_aptamers():
    """Загрузка RNA аптамеров из aptabench_rna_final.csv"""
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///aptabench_rna_final.csv' AS row
          CALL(row) {
              MERGE (n:rna {
                name: row.name,
                content: row.content
                })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ RNA аптамеры загружены")


async def upload_small_molecules():
    """Загрузка малых молекул из aptabench_small_molecules_final.csv"""
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///aptabench_small_molecules_final.csv' AS row
          CALL(row) {
              MERGE (n:small_molecule {
                name: row.name,
                content: row.content
                })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ Малые молекулы загружены")


def upload_interactions():
    """Загрузка взаимодействий между аптамерами и малыми молекулами из aptabench_df_merged.csv"""
    query = """
          LOAD CSV WITH HEADERS FROM 'file:///aptabench_df_merged.csv' AS row
          CALL(row) {
              WITH row WHERE row.type = 'DNA'
              MATCH (d:dna {name: row.aptamer_name}),
                    (s:small_molecule {name: row.small_molecule_name})
              MERGE (d)-[:interacts_with {
                  pKd_value: toFloat(row.pKd_value),
                  label: toInteger(row.label),
                  buffer: coalesce(row.buffer, 'NaN'),
                  origin: coalesce(row.origin, 'NaN'),
                  source: row.source
              }]-(s)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ DNA-молекула взаимодействия загружены")

    query = """
          LOAD CSV WITH HEADERS FROM 'file:///aptabench_df_merged.csv' AS row
          CALL(row) {
              WITH row WHERE row.type = 'RNA'
              MATCH (r:rna {name: row.aptamer_name}),
                    (s:small_molecule {name: row.small_molecule_name})
              MERGE (r)-[:interacts_with {
                  pKd_value: toFloat(row.pKd_value),
                  label: toInteger(row.label),
                  buffer: coalesce(row.buffer, 'NaN'),
                  origin: coalesce(row.origin, 'NaN'),
                  source: row.source
              }]-(s)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    print("✓ RNA-молекула взаимодействия загружены")


async def main():
    print("=" * 60)
    print("Загрузка данных AptaBench в Neo4j")
    print("=" * 60)
    
    # Параллельная загрузка узлов
    print("\n[1/2] Загрузка узлов...")
    tasks = [
        asyncio.create_task(upload_dna_aptamers()),
        asyncio.create_task(upload_rna_aptamers()),
        asyncio.create_task(upload_small_molecules()),
    ]
    await asyncio.gather(*tasks)

    # Последовательная загрузка связей
    print("\n[2/2] Загрузка связей...")
    upload_interactions()
    
    print("\n" + "=" * 60)
    print("Загрузка завершена успешно!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

