# BioSensGraph: Predicting Biopolymer Interactions via Knowledge Graph Embedding on a Property Graph of Molecular Entities

This repository is designed for semi-automated launch for predicting connections in a biological knowledge graph. Its purpose is to find new recognizeable elements for analyzers. 
---

## Overview

- **Goal:** Predict novel `interacts_with` relations using knowledge graph embeddings (KGE).  
- **Frameworks:** PyTorch-BigGraph (PBG), DVC for experiment management.  
- **Compute:** Designed for SLURM-based clusters.  

---

## Installation and prepare env

1. **Install [uv](https://github.com/astral-sh/uv):**
2. **Synchronization of required libraries** 
  ```bash
    uv sync
  ```
3. **Set env**
  ```bash
    uv venv .vevn
  ```
4. **Installing the experiment manager and storage**
  ```bash
    uv pip install "dvc[s3]"
    apt install jq
  ```
## Runnung experiments
  On SLURM 
  Use the provided scripts in sbatch_task/. Each script sets SLURM resources and calls a DVC Experiment with operator selection.
  Pattern inside each *.sh:

  ```bash
  #!/bin/bash
  uv run dvc exp run -S "operator=<OPERATOR_NAME>" -S "train.workers=<NUMBER_CPU's>"
  ```

Submit a job, e.g. for the diagonal operator:

  ```bash
  sbatch sbatch_task/operator_diagonal.sh
  ```
