import json
import h5py
import torch
import pandas as pd
from collections import defaultdict
from pathlib import Path


def load_entity_names(entity_json_path):
    with open(entity_json_path, "rt") as f:
        return json.load(f)


def load_embeddings(emb_h5_path):
    with h5py.File(emb_h5_path, "r") as hf:
        return torch.from_numpy(hf["embeddings"][...]).float()


def load_operator(h5_path, dim, relation_idx=0):
    diagonal_path = f"model/relations/{relation_idx}/operator/rhs/diagonal"
    with h5py.File(h5_path, "r") as hf:
        if diagonal_path in hf:
            diagonal = torch.from_numpy(hf[diagonal_path][...]).float()
            if diagonal.shape == (dim,):
                return diagonal
        
        candidates = [
            f"model/relations/{relation_idx}/operator/rhs/weight",
            f"model/relations/{relation_idx}/operator/weight",
            f"model/relations/{relation_idx}/operator/matrix",
            f"model/relations/{relation_idx}/weight",
            "model/operator/weight",
        ]
        for key in candidates:
            if key in hf:
                W = torch.from_numpy(hf[key][...]).float()
                if tuple(W.shape) == (dim, dim):
                    return W
        
        target = None
        def visit(name, obj):
            nonlocal target
            if target is None and isinstance(obj, h5py.Dataset):
                if obj.shape == (dim, dim) and "operator" in name.lower():
                    target = torch.from_numpy(obj[...]).float()
        hf.visititems(visit)
        if target is not None:
            return target
    
    raise RuntimeError(f"Operator not found in H5 (relation_idx={relation_idx})")


def load_test_pairs(test_path):
    df = pd.read_csv(test_path, sep="\t", header=None, names=["source", "relation", "target"])
    df["source"] = df["source"].astype(str)
    df["target"] = df["target"].astype(str)
    return list(zip(df["source"].tolist(), df["target"].tolist()))


def load_all_neighbors(train_path, val_path, test_path, relation_name="interacts_with"):
    all_neighbors = defaultdict(set)
    
    for path, name in [(train_path, "train"), (val_path, "val"), (test_path, "test")]:
        try:
            df = pd.read_csv(path, sep="\t", header=None, names=["source", "relation", "target"])
            df["source"] = df["source"].astype(str)
            df["target"] = df["target"].astype(str)
            df_filtered = df[df["relation"] == relation_name]
            for _, row in df_filtered.iterrows():
                all_neighbors[row["source"]].add(row["target"])
        except Exception as e:
            print(f"Error loading {name}: {e}")
    
    return all_neighbors


def load_csv_nodes(csv_path, entity_to_idx):
    df = pd.read_csv(csv_path)
    id_col = "id" if "id" in df.columns else "id_neo4j"
    name_col = "name" if "name" in df.columns else ("name_entity" if "name_entity" in df.columns else None)
    
    df["entity_id"] = df[id_col].astype(str)
    df["entity_idx"] = df["entity_id"].map(entity_to_idx)
    df_valid = df[df["entity_idx"].notna()].copy()
    df_valid["entity_idx"] = df_valid["entity_idx"].astype(int)
    
    if name_col:
        df_valid["entity_name"] = df_valid[name_col]
    else:
        df_valid["entity_name"] = df_valid["entity_id"]
    
    return df_valid

