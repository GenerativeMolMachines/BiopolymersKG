from neo4j import GraphDatabase

import tqdm
import numpy as np
import pandas as pd


db_api = "neo4j://77.234.216.102:7687"
db_login = "neo4j"
db_password = "bKJ2ONAjy1FdYuM"

driver = GraphDatabase.driver(
    db_api,
    auth=(db_login, db_password)
)
driver.verify_connectivity()

def upload_proteins():
    protein_data = pd.read_csv('biogrid/protein_data_biogrid.csv')
    protein_data.replace(np.nan, None, inplace=True)

    ds_dict = protein_data.to_dict("records")
    with driver.session(database="neo4j") as session:
        for item in tqdm(ds_dict):
            query = f"MERGE (n:protein "
            query += '{name: $name, representation_type: $representation_type, content: $content'
            if item['annotation']:
                query += ', annotation: $annotation)}'
                session.run(
                    query,
                    name=item['name'],
                    representation_type=item['representation_type'],
                    content=item['content'],
                    annotation=item['annotation'],
                )
            else:
                query += '})'
                session.run(
                    query,
                    name=item['name'],
                    representation_type=item['representation_type'],
                    content=item['content'],
                )


def upload_interactions():
    protein_protein_interaction = pd.read_csv('biogrid/protein_protein_interaction.csv')
    ds_dict = protein_protein_interaction.replace(np.nan, None).to_dict("records")
    with driver.session(database="neo4j") as session:
        for item in tqdm(ds_dict):
            raw_query = f"""
            MATCH (first:protein),(second:protein)
            WHERE first.name="{item['protein_name_a']}" AND second.name="{item['protein_name_b']}"
            """
            kwargs = {}
            args = []
            if item['Score']:
                args.append('score: $Score')
                kwargs['Score'] = item['Score']

            if args:
                args_string = '{' + ', '.join(args) + '}'
                raw_query += f"CREATE (first)-[:interacts_with {args_string}]->(second)"
                session.run(raw_query, **kwargs)
            else:
                raw_query += "CREATE (first)-[:interacts_with]->(second)"
                session.run(raw_query)