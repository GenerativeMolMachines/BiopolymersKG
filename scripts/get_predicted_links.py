import pandas as pd
from pathlib import Path
import gc

# apt_prot_model

# apt-sm
# rna-rna
# prot-prot
# prot-dna

DATA_PATH = "data/link_prediction/"
ENTITIES_PATH = DATA_PATH + "entities/"


def get_rna_sm_links():
    rna_df = pd.read_csv(ENTITIES_PATH + "rna.csv")
    sm_df = pd.read_csv(ENTITIES_PATH + "small_molecule.csv")

    existing_links = pd.read_csv(DATA_PATH + "existing_links/rna_sm.csv")

    links = rna_df[['nodeid']].merge(sm_df[['nodeid']], how='cross')

    idx1 = pd.MultiIndex.from_frame(links[['nodeid_x', 'nodeid_y']])
    idx2 = pd.MultiIndex.from_frame(existing_links[['nodeid_1', 'nodeid_2']])
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
    idx2 = pd.MultiIndex.from_frame(existing_links[['nodeid_1', 'nodeid_2']])
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


def main():
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


if __name__ == "__main__":
    main()