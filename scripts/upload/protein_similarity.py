import os
import dotenv
import pandas as pd
from neo4j import GraphDatabase

dotenv.load_dotenv()


db_api = os.environ["NEO4J_URL"]
db_login = os.environ["NEO4J_USER"]
db_password = os.environ["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(db_api, auth=(db_login, db_password))
driver.verify_connectivity()


def prepare_data():
    """
    Объединяет aligned_pairs.csv с protein_ids.csv для получения node IDs.
    
    Структура файлов:
    - aligned_pairs.csv: name_1, sequence_1, name_2, sequence_2, identity
    - protein_ids.csv: nodeid, content, name
    
    Мержим по двум колонкам (name И sequence) для точного совпадения.
    """
    # Загружаем данные о парах выровненных белков
    aligned_pairs = pd.read_csv("data/aligned_pairs.csv")
    print(f"Загружено {len(aligned_pairs)} пар выровненных белков")
    
    # Загружаем соответствие protein_name + sequence -> nodeid
    protein_ids = pd.read_csv("data/protein_ids.csv")
    print(f"Загружено {len(protein_ids)} белков с nodeid")
    
    # Объединяем для первого белка (name_1 + sequence_1)
    merged = aligned_pairs.merge(
        protein_ids,
        left_on=['name_1', 'sequence_1'],
        right_on=['name', 'content'],
        how='inner'
    )
    merged = merged.rename(columns={'nodeid': 'nodeid_1'})
    merged = merged.drop(columns=['name', 'content'])
    
    # Объединяем для второго белка (name_2 + sequence_2)
    merged = merged.merge(
        protein_ids,
        left_on=['name_2', 'sequence_2'],
        right_on=['name', 'content'],
        how='inner',
        suffixes=('', '_2')
    )
    merged = merged.rename(columns={'nodeid': 'nodeid_2'})
    merged = merged.drop(columns=['name', 'content'])
    
    # Выбираем только необходимые колонки: nodeid_1, nodeid_2, identity
    result = merged[['nodeid_1', 'nodeid_2', 'identity']].copy()
    
    # Сохраняем результат для загрузки в Neo4j
    output_path = "protein_similarity_nodeids.csv"
    result.to_csv(output_path, index=False)
    
    print(f"Подготовлено {len(result)} пар белков со сходством")
    print(f"Данные сохранены в {output_path}")
    
    return output_path


def upload_protein_similarity():
    """
    Загружает данные о сходстве белков в Neo4j.
    Создает ненаправленные отношения has_similarity между белками.
    """
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///protein_similarity_nodeids_high_score.csv' AS row
          CALL(row) {
              MATCH (p1:protein) WHERE id(p1) = toInteger(row.nodeid_1)
              MATCH (p2:protein) WHERE id(p2) = toInteger(row.nodeid_2)
              MERGE (p1)-[:has_similarity {score: toFloat(row.identity)}]-(p2)
          } IN TRANSACTIONS OF 1000 ROWS
    """
    with driver.session() as session:
        session.run(query)
    
    print("Сходство белков успешно загружено в базу данных")


def main():
    # print("Подготовка данных...")
    # prepare_data()
    
    print("\nЗагрузка в Neo4j...")
    upload_protein_similarity()
    
    print("\nГотово!")


if __name__ == "__main__":
    main()
