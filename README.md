# BiopolymersKnowledgeGraphs

## Overview
This project aims to develop a system that uses knowledge graph-based embeddings and machine learning techniques to analyze peptides. 

The main problem is the lack of an integrated approach that takes into account both local properties (structure, sequence) and global context (interactions, annotations, biochemical characteristics). 

To solve this problem, knowledge graphs are used to combine heterogeneous data from ontologies, textual annotations and structural characteristics of molecules. The application of knowledge graph embeddings methods allows the transformation of relationships between peptides into a vector space, and graph neural network models provide aggregation of local and global contexts for property prediction. 

Additionally, language models to describe peptide sequences are included in the vectorization process, and their embeddings are combined with representations derived from knowledge graphs. Further analysis will evaluate how this combination will affect the quality of peptide property prediction.

The established system will allow the integration of heterogeneous data on peptides, providing a more complete representation of their properties and the context of their interactions. This opens up new possibilities for repurposing known peptides, allowing to find new biomedical applications based on hidden patterns.

## Project Structure
```
BiopolymersKG/
├── graph_link_prediction_pbg/      # Main scalable link prediction system (PyTorch-BigGraph)
│   ├── conf/                       # Hydra configs
│   ├── sbatch_tasks/               # HPC execution scripts
│   ├── inference/                  # Inference, scoring, evaluation
│   ├── pbg_configs/                # PBG dataset & training configuration
│   ├── data/                       # Managed with DVC
│   └── results/                    # Model outputs, embeddings, metrics
│
├── graph_link_prediction_pykeen/   # Experimental link prediction system (PyKEEN)
│   ├── src/train/                  # RotatE, DistMult etc.
│   ├── download_data_from_neo4j/   # Graph extraction
│   └── splitting/                  # Dataset splitting utilities
│
├── scripts/                        # Neo4j upload and data processing tools
├── src/                            # Data models, parsers (UniProt, PDB, AlphaFold)
├── notebooks/                      # Analysis and exploratory notebooks
└── docs/                           # Documentation
```

## Link Prediction
Link prediction is one of the core machine learning tasks in this project. It enables the model to identify **missing**, **hidden**, or **previously unknown** interactions between biopolymers based on the structure of the knowledge graph.

## 1. Transductive Dataset Split

The graph is prepared using a **transductive split**, meaning:

- All **entities (nodes)** are present during training, validation, and testing.
- Only **edges (triples)** are divided into:
  - **80%** — training triples  
  - **10%** — validation triples  
  - **10%** — test triples  

This setup evaluates the model’s ability to **recover missing interactions** among already known entities.

Triples are stored in TSV format: ```lhs_entity_id relation_type rhs_entity_id```

Supported relations:

- `interacts_with`
- `has_similarity`
Targeted binding for finding new molecular interactions - `interaction with`
---

## 2. PyTorch-BigGraph (PBG) Training Pipeline

PBG is used for scalable training on graphs with millions of nodes and tens of millions of edges.

### 2.1 Graph Partitioning

PBG automatically partitions the graph:

- Enables training on datasets larger than GPU/CPU memory.
- Supports distributed and parallel training.
- Ensures efficient negative sampling.
- Allows streaming of partitions instead of loading the whole graph into memory.

Each relation is parameterized by a trained **operator** (e.g., diagonal, affine, complex diagonal).

---

### 2.2 Optimization Objective

For every true triple \(h, r, t), PBG computes a **score**:

score = f(h, r, t)

where:

- \(h\) is the head entity embedding  
- \(t\) is the tail entity embedding  
- \(r\) is a relation-specific operator

Higher scores correspond to plausible/true interactions.

Training uses **MarginRankingLoss**:

Loss = max(0, margin - score_positive + score_negative)

Where:

- \(h, r, t) is a positive triple  
- \(h', r, t') is a negative (corrupted) triple  
- \(margin) is the margin hyperparameter  

The model learns to assign:

- **higher** scores to true triples  
- **lower** scores to corrupted triples  

---

## 3. Negative Sampling

PBG uses **hybrid negative sampling**, combining both *batch-based* and *uniform* negatives.

### 3.1 Batch Negatives

These are generated from entity IDs inside the current minibatch.

**Advantages:**

- Computationally efficient  
- Reflects local graph structure  
- Scales well with large datasets  

### 3.2 Uniform Negatives

Sampled uniformly from **all entities** in the graph.

**Advantages:**

- Introduces global contrast  
- Prevents embedding collapse  
- Improves ranking metrics  

**Configuration used in this project:**

- **50 batch negatives**
- **100 uniform negatives**

Thus, each positive triple is trained against **≈150 negatives**, strengthening contrastive learning.

---

## 4. What the Model Learns

### 4.1 Entity Embeddings

Dense vector representations (typically **400 dimensions**) for:

- peptides  
- proteins   
- DNA / RNA  
- small molecules  

These embeddings encode both local and global graph structure.

---

### 4.2 Relation Operators

Operators transform a head entity embedding before comparison with the tail:

- **Diagonal** - elementwise scaling  
- **Affine** - linear transformation + bias  
- **ComplexDiagonal** - rotation in complex space  
- **Translation** - vector translation (TransE-style)  

Each relation learns its own operator parameters.

---

### 4.3 Comparator (Score Function)

Defines how similarity is computed between the transformed head embedding and the tail embedding:

- **Cosine similarity**
- **Dot product**
- **L2 distance**
- **Squared L2 distance**
---

## 5. Evaluation Protocol

Since link prediction is fundamentally a **ranking problem**, we use standard ranking metrics:

- **MRR** - Mean Reciprocal Rank  
- **Hits@K** - K ∈ {1, 5, 10}  
- **Precision@K**, **Recall@K**, **F1@K**  
- **MAP** - Mean Average Precision  
- **NDCG@K** - Normalized Discounted Cumulative Gain  

Each test triple \(h, r, t) is evaluated by ranking:

- the true tail \(t) among **corrupted tails**, or  
- the true head \(h) among **corrupted heads**  
---

## 6. Inference Pipeline

The inference module provides:

1. Loading of trained embeddings and relation operators  
2. Querying the graph with any entity and relation type  
3. Computing scores against all candidate tail entities  
4. Returning a **ranked list of predicted links**  
5. Optional evaluation using the same negative sampling strategy as training  

**Applications:**

- discovery of peptide–protein or protein–molecule interactions  
- hit identification in early-stage molecular screening  
- peptide repurposing across biological functions  
- biosensor and analyte recognition modeling  

---

## Database
The project utilizes [neo4j](https://neo4j.com/) graph database management system.

### Basic queries
[Documentation](https://neo4j.com/docs/cypher-cheat-sheet)

Count all records
```cypher
MATCH (n) RETURN COUNT(n)
```

Get statistics for all nodes with labels
```cypher
MATCH (n) RETURN DISTINCT LABELS(n), COUNT(n)
```

Get statistics for all nodes interactions
```cypher
MATCH (n)-[r:interacts_with]->(m) RETURN COUNT(r) AS relationship_count, LABELS(n) AS source_labels, LABELS(m) AS dest_labels ORDER BY relationship_count DESC 
```

## [File layout](docs/file_layout.md)
