Node labels statistics
```cypher
MATCH (n) RETURN DISTINCT LABELS(n), COUNT(n)
```

Node labels interaction statistics
```cypher
MATCH (n)-[r:interacts_with]->(m) RETURN COUNT(r) AS relationship_count, LABELS(n) AS source_labels, LABELS(m) AS dest_labels ORDER BY relationship_count DESC 
```
