# File Description

## scripts
- [upload_binding_db.py](../scripts/upload_binding_db.py) - script for uploading data from the binding_db database
- [upload_biogrid.py](../scripts/upload_biogrid.py) - script for uploading data from the biogrid database

## notebooks
- [check_duplicates.ipynb](../notebooks/check_duplicates.ipynb) - notebook for checking data overlaps between datasets in the source files
- [clean_small_molecule_data.ipynb](../notebooks/clean_small_molecule_data.ipynb) - notebook for validating small molecule data using the [rdkit](https://www.rdkit.org/) library and removing invalid data from the database
- [count_data.ipynb](../notebooks/count_data.ipynb) - notebook for counting the number of samples of each class and subclass of substances among the data obtained at the initial data collection stage
- [preparation.ipynb](../notebooks/preparation.ipynb) - notebook for preprocessing data obtained at the initial data collection stage
- [upload.ipynb](../notebooks/upload.ipynb) - notebook for uploading data obtained at the initial data collection stage to the database