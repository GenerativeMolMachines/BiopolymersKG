# BiopolymersKnowledgeGraphs

## Overview
This project aims to develop a system that uses knowledge graph-based embeddings and machine learning techniques to analyze peptides. 

The main problem is the lack of an integrated approach that takes into account both local properties (structure, sequence) and global context (interactions, annotations, biochemical characteristics). 

To solve this problem, knowledge graphs are used to combine heterogeneous data from ontologies, textual annotations and structural characteristics of molecules. The application of knowledge graph embeddings methods allows the transformation of relationships between peptides into a vector space, and graph neural network models provide aggregation of local and global contexts for property prediction. 

Additionally, language models to describe peptide sequences are included in the vectorization process, and their embeddings are combined with representations derived from knowledge graphs. Further analysis will evaluate how this combination will affect the quality of peptide property prediction.

The established system will allow the integration of heterogeneous data on peptides, providing a more complete representation of their properties and the context of their interactions. This opens up new possibilities for repurposing known peptides, allowing to find new biomedical applications based on hidden patterns

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

