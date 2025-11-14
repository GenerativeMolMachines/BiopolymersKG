import os
import time
import hashlib
import dotenv
import pandas as pd

dotenv.load_dotenv()


def make_hash(value: str) -> str:
    return hashlib.md5(value.encode()).hexdigest()


def hash_df(df: pd.DataFrame, col1: str, col2: str, hash_label: str) -> pd.DataFrame:
    start = time.perf_counter()

    df = df.copy()
    df[f"{col1}_{col2}"] = df[col1] + df[col2]
    df[hash_label] = df[f"{col1}_{col2}"].apply(make_hash)
    df = df.drop(f"{col1}_{col2}", axis=1)

    end = time.perf_counter()

    print(f"Hashing {col1} {col2} to {hash_label} time: {end - start:.3f} s.")
    return df


def rename_entities(
    df: pd.DataFrame,
    nodeid_col: str,
    hash_col: str,
    node_df: pd.DataFrame
) -> pd.DataFrame:
    start = time.perf_counter()

    merged_df = df.merge(
        node_df[["nodeid", "hash"]],
        left_on=hash_col,
        right_on="hash",
    )
    merged_df.rename(columns={"nodeid": nodeid_col}, inplace=True)
    merged_df.drop("hash", axis=1, inplace=True)

    end = time.perf_counter()
    print(f"Merging nodeids for {nodeid_col} on {hash_col} time: {end - start:.3f} s.")

    return merged_df


def filter_similarity_df(df: pd.DataFrame) -> pd.DataFrame:
    filtered_df = df[~(
        (df["name_1"] == df["name_2"]) & (df["content_1"] == df["content_2"])
    )]
    return filtered_df


def hash_nodes_similarity(
    similarity_df: pd.DataFrame,
    nodes_df: pd.DataFrame,
) -> pd.DataFrame:
    nodes_hashed_df = hash_df(
        nodes_df,
        "name",
        "content",
        "hash",
    )
    print("rows before:", similarity_df.shape[0])
    similarity_hashed_df = hash_df(
        similarity_df,
        "name_1",
        "content_1",
        "hash_1",
    )
    similarity_hashed_df = hash_df(
        similarity_hashed_df,
        "name_2",
        "content_2",
        "hash_2",
    )
    merged_hash_df = rename_entities(
        similarity_hashed_df,
        "nodeid_1",
        "hash_1",
        nodes_hashed_df,
    )
    merged_hash_df = rename_entities(
        merged_hash_df,
        "nodeid_2",
        "hash_2",
        nodes_hashed_df,
    )
    print("rows after:", merged_hash_df.shape[0])
    return merged_hash_df


def rename_similarity():
    start = time.perf_counter()

    protein_nodes_df = pd.read_csv("data/entities/neo4j_proteins.csv")
    small_molecule_nodes_df = pd.read_csv("data/entities/neo4j_small_molecules.csv")
    dna_nodes_df = pd.read_csv("data/entities/db_dna.csv")
    rna_nodes_df = pd.read_csv("data/entities/db_rna.csv")

    dna_similarity = pd.read_csv("data/db_similarity/dna_similarity_80.csv")
    rna_similarity = pd.read_csv("data/db_similarity/rna_similarity_80.csv")
    protein_similarity = pd.read_csv("data/db_similarity/similarity_proteins.csv")
    small_molecule_similarity = pd.read_csv("data/db_similarity/similarity_small_molecule.csv")

    print(f"df reading time: {time.perf_counter() - start:.3f} s.")

    print("df filtering")
    dna_similarity = filter_similarity_df(dna_similarity)
    rna_similarity = filter_similarity_df(rna_similarity)
    protein_similarity = filter_similarity_df(protein_similarity)
    small_molecule_similarity = filter_similarity_df(small_molecule_similarity)
 
    print("df hash and merge")

    print("dna")
    hashed_dna_similarity = hash_nodes_similarity(dna_similarity, dna_nodes_df)

    print("rna")
    hashed_rna_similarity = hash_nodes_similarity(rna_similarity, rna_nodes_df)

    print("protein")
    hashed_protein_similarity = hash_nodes_similarity(protein_similarity, protein_nodes_df)

    print("small molecules")
    hashed_small_molecule_similarity = hash_nodes_similarity(
        small_molecule_similarity,
        small_molecule_nodes_df
    )

    print("df write")
    write_start = time.perf_counter()

    hashed_dna_similarity.to_csv("data/db_similarity/hashed/dna_similarity.csv")
    hashed_rna_similarity.to_csv("data/db_similarity/hashed/rna_similarity.csv")
    hashed_protein_similarity.to_csv("data/db_similarity/hashed/protein_similarity.csv")
    hashed_small_molecule_similarity.to_csv("data/db_similarity/hashed/small_molecule_similarity.csv")

    end = time.perf_counter()

    print(f"df write time: {end - write_start:.3f} s.")

    print(f"Total time: {end - start:.3f} s.")


if __name__ == "__main__":
    rename_similarity()

