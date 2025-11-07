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

    print(df.shape)
    print(df[df[hash_col].isin(node_df["hash"])].shape)

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


def main():
    start = time.perf_counter()

    protein_nodes_df = pd.read_csv("data/entities/neo4j_proteins.csv")
    small_molecule_nodes_df = pd.read_csv("data/entities/neo4j_small_molecules.csv")
    binding_db_df = pd.read_csv("~/Downloads/processed_binding_db 2/binding_db_interactions_unique.csv")
    
    print(f"df reading time: {time.perf_counter() - start:.3f} s.")
    
    print("protein hash")
    protein_nodes_hashed_df = hash_df(
        protein_nodes_df,
        "name",
        "content",
        "hash"
    )

    print("small molecules hash")
    small_molecule_nodes_hashed_df = hash_df(
        small_molecule_nodes_df,
        "name",
        "content",
        "hash"
    )

    print("protein hash in interactions")
    binding_db_hashed_df = hash_df(
        binding_db_df,
        "protein_name",
        "protein_sequence",
        "protein_hash"
    )

    print("small molecule hash in interactions")
    binding_db_hashed_df = hash_df(
        binding_db_hashed_df,
        "molecule_name",
        "molecule_smiles",
        "molecule_hash"
    )

    print("merge for proteins")
    merged_binding_df = rename_entities(
        binding_db_hashed_df,
        "protein_nodeid",
        "protein_hash",
        protein_nodes_hashed_df,
    )

    print("merge for small molecules")
    merged_binding_df = rename_entities(
        merged_binding_df,
        "molecule_nodeid",
        "molecule_hash",
        small_molecule_nodes_hashed_df,
    )

    write_start = time.perf_counter()

    merged_binding_df.to_csv("data/binding_db_interactions_nodeids.csv")
    end = time.perf_counter()

    print(f"df write time: {end - write_start:.3f} s.")

    print(f"Total time: {end - start:.3f} s.")


if __name__ == "__main__":
    main()

