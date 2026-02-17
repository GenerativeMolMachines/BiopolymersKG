import os
import dotenv
import asyncio
import pandas as pd
from neo4j import GraphDatabase

dotenv.load_dotenv()


db_api = os.environ["NEO4J_URL"]
db_login = os.environ["NEO4J_USER"]
db_password = os.environ["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(db_api, auth=(db_login, db_password))
driver.verify_connectivity()


def prepare_protein_condition_with_nodeids():
    """
    Подготавливает файл protein_condition с nodeid для быстрой загрузки.
    """
    print("Подготовка protein_condition с nodeid...")
    
    # Загружаем данные
    protein_condition = pd.read_csv("data/biomarkers/protein_condition.csv")
    protein_ids = pd.read_csv("data/protein_ids.csv")
    
    # Объединяем по name и content
    merged = protein_condition.merge(
        protein_ids[['nodeid', 'name', 'content']],
        on=['name', 'content'],
        how='inner'
    )
    
    # Фильтруем только строки с валидным content
    merged = merged[merged['content'].notna()]
    
    # Выбираем нужные колонки
    result = merged[['nodeid', 'conditions', 'indication_types', 'sex', 'biofluid']]
    
    # Сохраняем
    output_path = "data/biomarkers/protein_condition_nodeids.csv"
    result.to_csv(output_path, index=False)
    
    print(f"  Подготовлено {len(result)} записей -> {output_path}")
    return output_path


def prepare_chemical_condition_with_nodeids():
    """
    Подготавливает файл chemical_condition с nodeid для быстрой загрузки.
    """
    print("Подготовка chemical_condition с nodeid...")
    
    # Загружаем данные
    chemical_condition = pd.read_csv("data/biomarkers/chemical_condition.csv")
    small_molecules_ids = pd.read_csv("data/small_molecules_nodeids.csv")
    
    # Объединяем по name и content
    merged = chemical_condition.merge(
        small_molecules_ids[['nodeid', 'name', 'content']],
        on=['name', 'content'],
        how='inner'
    )
    
    # Фильтруем только строки с валидным content
    merged = merged[merged['content'].notna()]
    
    # Выбираем нужные колонки
    result = merged[['nodeid', 'conditions', 'indication_types', 'sex', 'biofluid']]
    
    # Сохраняем
    output_path = "data/biomarkers/chemical_condition_nodeids.csv"
    result.to_csv(output_path, index=False)
    
    print(f"  Подготовлено {len(result)} записей -> {output_path}")
    return output_path


def prepare_protein_condition_nci_with_nodeids():
    """
    Подготавливает файл protein_condition_nci_db с nodeid для быстрой загрузки.
    """
    print("Подготовка protein_condition_nci_db с nodeid...")
    
    # Загружаем данные
    protein_condition_nci = pd.read_csv("data/biomarkers/protein_condition_nci_db.csv")
    protein_ids = pd.read_csv("data/protein_ids.csv")
    
    # Объединяем по name и content
    merged = protein_condition_nci.merge(
        protein_ids[['nodeid', 'name', 'content']],
        on=['name', 'content'],
        how='inner'
    )
    
    # Фильтруем только строки с валидным content
    merged = merged[merged['content'].notna()]
    
    # Выбираем нужные колонки
    result = merged[['nodeid', 'conditions']]
    
    # Сохраняем
    output_path = "data/biomarkers/protein_condition_nci_db_nodeids.csv"
    result.to_csv(output_path, index=False)
    
    print(f"  Подготовлено {len(result)} записей -> {output_path}")
    return output_path


async def upload_protein_biomarkers():
    """
    Загружает уникальные белки-биомаркеры в Neo4j.
    Структура файла: name, uniprot_id, content
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///biomarkers/unique_protein_biomarkers.csv' AS row
          CALL(row) {
              WITH row WHERE row.content IS NOT NULL
              MERGE (p:protein {
                name: row.name,
                content: row.content
              })
              SET p.uniprot_id = row.uniprot_id
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    
    print("Загружены белки-биомаркеры")


async def upload_chemical_biomarkers():
    """
    Загружает уникальные химические биомаркеры (малые молекулы) в Neo4j.
    Структура файла: name, hmdb_id, content
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///biomarkers/unique_chemical_biomarkers.csv' AS row
          CALL(row) {
              WITH row WHERE row.content IS NOT NULL
              MERGE (m:small_molecule {
                name: row.name,
                content: row.content
              })
              SET m.hmdb_id = row.hmdb_id
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    
    print("Загружены химические биомаркеры")


async def upload_conditions():
    """
    Загружает уникальные условия (болезни, состояния) в Neo4j.
    Структура файла: conditions (одна колонка с названием условия)
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///biomarkers/unique_conditions.csv' AS row
          CALL(row) {
              MERGE (c:condition {
                name: row.conditions
              })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    
    print("Загружены условия (conditions)")


def upload_protein_condition_relations():
    """
    Загружает связи между белками и условиями используя nodeid.
    Структура файла: nodeid, conditions, indication_types, sex, biofluid
    
    Связи создаются как protein-[:biomarker_for]->condition с атрибутами.
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///biomarkers/protein_condition_nodeids.csv' AS row
          CALL(row) {
              MATCH (p:protein) WHERE id(p) = toInteger(row.nodeid)
              MATCH (c:condition {name: row.conditions})
              MERGE (p)-[:biomarker_for {
                indication_type: coalesce(row.indication_types, 'NaN'),
                sex: coalesce(row.sex, 'NaN'),
                biofluid: coalesce(row.biofluid, 'NaN')
              }]->(c)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    
    print("Загружены связи белок-условие")


def upload_chemical_condition_relations():
    """
    Загружает связи между химическими биомаркерами и условиями используя nodeid.
    Структура файла: nodeid, conditions, indication_types, sex, biofluid
    
    Связи создаются как small_molecule-[:biomarker_for]->condition с атрибутами.
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///biomarkers/chemical_condition_nodeids.csv' AS row
          CALL(row) {
              MATCH (m:small_molecule) WHERE id(m) = toInteger(row.nodeid)
              MATCH (c:condition {name: row.conditions})
              MERGE (m)-[:biomarker_for {
                indication_type: coalesce(row.indication_types, 'NaN'),
                sex: coalesce(row.sex, 'NaN'),
                biofluid: coalesce(row.biofluid, 'NaN')
              }]->(c)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    
    print("Загружены связи химикат-условие")


async def upload_proteins_nci_db():
    """
    Загружает белки из NCI DB.
    Структура файла: name, class, content
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///biomarkers/unique_proteins_nci_db.csv' AS row
          CALL(row) {
              WITH row WHERE row.content IS NOT NULL
              MERGE (p:protein {
                name: row.name,
                content: row.content
              })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    
    print("Загружены белки из NCI DB")


async def upload_conditions_nci_db():
    """
    Загружает условия из NCI DB.
    Структура файла: conditions
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///biomarkers/unique_conditions_nci_db.csv' AS row
          CALL(row) {
              MERGE (c:condition {
                name: row.conditions
              })
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    
    print("Загружены условия из NCI DB")


def upload_protein_condition_nci_db_relations():
    """
    Загружает связи между белками и условиями из NCI DB используя nodeid.
    Структура файла: nodeid, conditions
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///biomarkers/protein_condition_nci_db_nodeids.csv' AS row
          CALL(row) {
              MATCH (p:protein) WHERE id(p) = toInteger(row.nodeid)
              MATCH (c:condition {name: row.conditions})
              MERGE (p)-[:biomarker_for]->(c)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    
    print("Загружены связи белок-условие из NCI DB")


async def main():
    print("=== Загрузка биомаркеров ===\n")
    
    print("Этап 0: Подготовка данных с nodeid...")
    # prepare_protein_condition_with_nodeids()
    # prepare_chemical_condition_with_nodeids()
    # prepare_protein_condition_nci_with_nodeids()

    print("\nЭтап 1: Загрузка узлов из основных источников...")
    # Загружаем все узлы параллельно
    tasks = [
        asyncio.create_task(upload_protein_biomarkers()),
        asyncio.create_task(upload_chemical_biomarkers()),
        asyncio.create_task(upload_conditions()),
    ]
    await asyncio.gather(*tasks)
    
    print("\nЭтап 2: Загрузка узлов из NCI DB...")
    tasks_nci = [
        asyncio.create_task(upload_proteins_nci_db()),
        asyncio.create_task(upload_conditions_nci_db()),
    ]
    await asyncio.gather(*tasks_nci)
    
    print("\nЭтап 3: Загрузка связей...")
    # Загружаем связи после того, как все узлы созданы
    upload_protein_condition_relations()
    upload_chemical_condition_relations()
    upload_protein_condition_nci_db_relations()
    
    print("\n=== Загрузка завершена успешно! ===")


if __name__ == "__main__":
    asyncio.run(main())
