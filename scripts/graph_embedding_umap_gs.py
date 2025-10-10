import os
import json
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

from tqdm import tqdm

import umap
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

import seaborn as sns
import matplotlib.pyplot as plt

PWD = Path(__file__).parent.parent

with open(PWD / "data/ids_with_types.json", "r") as f:
    ids_with_types = json.load(f)

with h5py.File(PWD / "data/embeddings_molecules_0.v224.h5", "r") as f:
    print("File keys:", f.keys())
    embeddings = np.array(f['embeddings'], dtype=np.float32)
    optimizers = np.array(f['optimizer'])

print("Data loaded")

param_grid = {
    'n_neighbors': [5, 10, 15,],
    'min_dist': [0.0, 0.1, 0.4, 0.7],
    'n_components': [2, 3],
    'metric': ['euclidean', 'cosine']
}

grid = ParameterGrid(param_grid)

results = []

random_state = 242

expected_num_clusters = len(set(ids_with_types.values()))

for params in tqdm(grid, desc="UMAP grid search"):
    reducer = umap.UMAP(
        n_neighbors=params['n_neighbors'],
        min_dist=params['min_dist'],
        n_components=params['n_components'],
        metric=params['metric'],
    )

    reduced_embedding = reducer.fit_transform(embeddings)

    # Use KMeans for evaluation
    kmeans = KMeans(n_clusters=expected_num_clusters, random_state=random_state)
    cluster_labels = kmeans.fit_predict(reduced_embedding)
    
    # Evaluate with silhouette score
    score = silhouette_score(reduced_embedding, cluster_labels)
    
    results.append((params, score))

results.sort(key=lambda x: x[1], reverse=True)

# Best result
best_params, best_score = results[0]
print("Best UMAP params:", best_params)
print("Best silhouette score:", best_score)

with open(PWD / "results/ge_umap_gs.json", "w") as f:
    json.dump(results, f, indent=4)