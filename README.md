# BiopolymersKnowledgeGraphs

## Overview
This project aims to develop a system that uses knowledge graph-based embeddings and machine learning techniques to analyze peptides. 

The main problem is the lack of an integrated approach that takes into account both local properties (structure, sequence) and global context (interactions, annotations, biochemical characteristics). 

To solve this problem, knowledge graphs are used to combine heterogeneous data from ontologies, textual annotations and structural characteristics of molecules. The application of knowledge graph embeddings methods allows the transformation of relationships between peptides into a vector space, and graph neural network models provide aggregation of local and global contexts for property prediction. 

Additionally, language models to describe peptide sequences are included in the vectorization process, and their embeddings are combined with representations derived from knowledge graphs. Further analysis will evaluate how this combination will affect the quality of peptide property prediction.

The established system will allow the integration of heterogeneous data on peptides, providing a more complete representation of their properties and the context of their interactions. This opens up new possibilities for repurposing known peptides, allowing to find new biomedical applications based on hidden patterns


## Link Prediction
The project implements link prediction to uncover hidden interactions within the knowledge graph. There are two implementations available:

### 1. PyTorch-BigGraph (PBG) - Main Implementation
Located in `graph_link_prediction_pbg/`.

This is the primary implementation designed for **Big Data** and large-scale graphs. It utilizes [PyTorch-BigGraph](https://github.com/facebookresearch/PyTorch-BigGraph) to efficiently train embeddings on massive datasets that do not fit into memory.

**Key features:**
- Scalable training on large graphs.
- Efficient memory usage with partitioned training.
- Configuration via `conf/` and `params.yaml`.
- Dependency management via `uv`.

### 2. PyKEEN - Experimental/Development
Located in `graph_link_prediction_pykeen/`.

This implementation uses [PyKEEN](https://github.com/pykeen/pykeen) and is currently under development. It serves as a testbed for new models and research experiments but is not yet optimized for the full-scale dataset.

### Usage
Both implementations use `uv` for dependency management.

To work with PBG:
```bash
cd graph_link_prediction_pbg
uv sync
uv run sbatch_tasks/operator_{}.sh
```

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
