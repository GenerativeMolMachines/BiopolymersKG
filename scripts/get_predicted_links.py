import os
import gc
import json
from pathlib import Path

import asyncio
import httpx
import dotenv
import pandas as pd

dotenv.load_dotenv()

# apt_prot_model

# apt-sm
# rna-rna
# prot-prot
# prot-dna

DATA_PATH = "data/link_prediction/"
ENTITIES_PATH = DATA_PATH + "entities/"
RESULT_PATH = DATA_PATH + "prediction_results/"


def get_rna_sm_links():
    rna_df = pd.read_csv(ENTITIES_PATH + "rna.csv")
    sm_df = pd.read_csv(ENTITIES_PATH + "small_molecule.csv")

    existing_links = pd.read_csv(DATA_PATH + "existing_links/rna_sm.csv")

    links = rna_df[['nodeid']].merge(sm_df[['nodeid']], how='cross')

    idx1 = pd.MultiIndex.from_frame(links[['nodeid_x', 'nodeid_y']])
    idx2 = pd.MultiIndex.from_frame(existing_links[['nodeid_rna', 'nodeid_sm']])
    links = links[~idx1.isin(idx2)]

    links.rename(
        columns={
            'nodeid_x': 'nodeid_rna',
            'nodeid_y': 'nodeid_sm'
        },
        inplace=True,
    )

    return links


def get_rna_rna_links():
    rna_df = pd.read_csv(ENTITIES_PATH + "rna.csv")

    links = rna_df[['nodeid']].merge(rna_df[['nodeid']], how='cross')
    links = links[links['nodeid_x'] != links['nodeid_y']]

    links.rename(
        columns={
            'nodeid_x': 'nodeid_1',
            'nodeid_y': 'nodeid_2'
        },
        inplace=True
    )

    return links


def get_prot_prot_links():
    prot_df = pd.read_csv(ENTITIES_PATH + "protein.csv")

    existing_links = pd.read_csv(DATA_PATH + "existing_links/prot_prot.csv")

    links = prot_df[['nodeid']].merge(prot_df[['nodeid']], how='cross')
    links = links[links['nodeid_x'] != links['nodeid_y']]

    idx1 = pd.MultiIndex.from_frame(links[['nodeid_x', 'nodeid_y']])
    idx2 = pd.MultiIndex.from_frame(existing_links[['nodeid_protein_1', 'nodeid_protein_2']])
    links = links[~idx1.isin(idx2)]

    links.rename(
        columns={
            'nodeid_x': 'nodeid_1',
            'nodeid_y': 'nodeid_2'
        },
        inplace=True
    )

    return links


def get_prot_dna_links():
    prot_df = pd.read_csv(ENTITIES_PATH + "protein.csv")
    dna_df = pd.read_csv(ENTITIES_PATH + "dna.csv")

    links = prot_df[['nodeid']].merge(dna_df[['nodeid']], how='cross')
    links.rename(
        columns={
            'nodeid_x': 'nodeid_protein',
            'nodeid_y': 'nodeid_dna'
        },
        inplace=True
    )

    return links


def shuffle_data():
    out_dir = Path(DATA_PATH) / "predicted_links"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = get_rna_sm_links()
    df.to_parquet(out_dir / "rna_sm.parquet.gzip", compression="gzip", index=False)
    del df
    gc.collect()

    df = get_rna_rna_links()
    df.to_parquet(out_dir / "rna_rna.parquet.gzip", compression="gzip", index=False)
    del df
    gc.collect()

    df = get_prot_prot_links()
    df.to_parquet(out_dir / "prot_prot.parquet.gzip", compression="gzip", index=False)
    del df
    gc.collect()

    df = get_prot_dna_links()
    df.to_parquet(out_dir / "prot_dna.parquet.gzip", compression="gzip", index=False)
    del df
    gc.collect()


def pair_generator(init_pairs: list[list[str]], num_pairs: int, batch_size: int=500):
    if not init_pairs or num_pairs <= 0:
        return
    
    for pair_range in range(0, min(num_pairs, len(init_pairs)), batch_size):
        yield ";".join([">".join(p) for p in init_pairs[pair_range:pair_range+batch_size]])


async def get_rna_sm_predictions():
    url = os.environ['RNA_SM_API']
    pairs = pd.read_parquet(DATA_PATH + "predicted_links/rna_sm.parquet.gzip")
    rna = pd.read_csv(ENTITIES_PATH + "rna.csv")
    sm = pd.read_csv(ENTITIES_PATH + "small_molecule.csv")
    pairs['rna_content'] = pairs.merge(rna[['nodeid', 'content']], left_on='nodeid_rna', right_on='nodeid', how='left')['content']
    pairs['sm_content'] = pairs.merge(sm[['nodeid', 'content']], left_on='nodeid_sm', right_on='nodeid', how='left')['content']
    pair_list = pairs[['rna_content', 'sm_content']].values.tolist()
    result = []
    async with httpx.AsyncClient(timeout=None) as client:
        i = 0
        for batch in pair_generator(pair_list, num_pairs=pairs.shape[0], batch_size=500):
            response = await client.post(url + "?rna_mol_smiles=" + batch)
            if not response.is_success:
                print("Error:", response.status_code, response.text)
                continue
            result.extend(response.json()["result"])
            i += 1

            if i % 10 == 0:
                with open(RESULT_PATH + "rna_sm_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4)

    return result


async def get_rna_rna_predictions():
    url = os.environ['RNA_RNA_API']
    pairs = pd.read_parquet(DATA_PATH + "predicted_links/rna_rna.parquet.gzip")
    rna = pd.read_csv(ENTITIES_PATH + "rna.csv")
    pairs['rna_1_content'] = pairs.merge(rna[['nodeid', 'content']], left_on='nodeid_1', right_on='nodeid', how='left')['content']
    pairs['rna_2_content'] = pairs.merge(rna[['nodeid', 'content']], left_on='nodeid_2', right_on='nodeid', how='left')['content']
    pair_list = pairs[['rna_1_content', 'rna_2_content']].values.tolist()
    result = []
    async with httpx.AsyncClient(timeout=None) as client:
        i = 0
        for batch in pair_generator(pair_list, num_pairs=pairs.shape[0], batch_size=500):
            response = await client.post(url + "?rna_mol_1_smiles=" + batch)
            if not response.is_success:
                print("Error:", response.status_code, response.text)
                continue
            result.extend(response.json()["result"])
            i += 1

            if i % 10 == 0:
                with open(RESULT_PATH + "rna_rna_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4)

    return result


async def get_prot_dna_predictions():
    url = os.environ['PROT_DNA_API']
    pairs = pd.read_parquet(DATA_PATH + "predicted_links/prot_dna.parquet.gzip")
    prot = pd.read_csv(ENTITIES_PATH + "protein.csv")
    dna = pd.read_csv(ENTITIES_PATH + "dna.csv")
    pairs['prot_content'] = pairs.merge(prot[['nodeid', 'content']], left_on='nodeid_protein', right_on='nodeid', how='left')['content']
    pairs['dna_content'] = pairs.merge(dna[['nodeid', 'content']], left_on='nodeid_dna', right_on='nodeid', how='left')['content']
    pair_list = pairs[['prot_content', 'dna_content']].values.tolist()
    result = []
    async with httpx.AsyncClient(timeout=None) as client:
        i = 0
        for batch in pair_generator(pair_list, num_pairs=pairs.shape[0], batch_size=500):
            response = await client.post(url + "?prot_mol_dna=" + batch)
            if not response.is_success:
                print("Error:", response.status_code, response.text)
                continue
            result.extend(response.json()["result"])
            i += 1

            if i % 10 == 0:
                with open(RESULT_PATH + "prot_dna_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4)

    return result



async def get_predictions():
    tasks = [
        get_rna_sm_predictions(),
        get_rna_rna_predictions(),
        get_prot_dna_predictions(),
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # shuffle_data()
    asyncio.run(get_predictions())
