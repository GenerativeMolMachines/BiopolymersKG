# Link Prediction with PyKEEN

This project implements link prediction on knowledge graphs using [PyKEEN](https://github.com/pykeen/pykeen).

## Structure

- `src/`: Source code for the project.
- `download_data_from_neo4j/`: Scripts for fetching data from Neo4j.
- `splitting/`: Scripts for splitting data into train/test/validation sets.
- `main.py`: Main entry point for training/evaluation.
- `*.ipynb`: Jupyter notebooks for analysis and experimentation.
- `distmult.sh`, `rotate.sh`: Shell scripts for running specific models.

## Installation & Management

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and python version handling.

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.

### Setup

Sync the project to create the virtual environment and install dependencies from `pyproject.toml`:

```bash
uv sync
```

This command will automatically set up a Python virtual environment (defaulting to Python 3.12+ as specified in configuration) and install all required packages.

## Usage

Run scripts using `uv run` to execute them within the project's isolated environment.

1. **Prepare Data**:
   ```bash
   uv run prepare_data_iw_hs.py
   ```

2. **Run Training**:
   ```bash
   uv run main.py
   ```

3. **Running Scripts**:
   If you use the shell scripts (e.g., `rotate.sh`), ensure they call python via `uv run` or use the activated environment.
   
   Example `rotate.sh` execution:
   ```bash
   bash rotate.sh
   ```

4. **Adding Dependencies**:
   To add a new library:
   ```bash
   uv add pandas
   ```

## Dependencies

Main dependencies include:
- `pykeen`
- `neo4j`
- `pandas`
- `networkx`
- `matplotlib`
- `seaborn`
- `plotly`

See `pyproject.toml` for the complete list and versions.

