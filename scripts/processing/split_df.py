import os
import dotenv
import pandas as pd

dotenv.load_dotenv()


PREPARED_DATA_PATH = "data/reparsing/prepared"


def get_entity_df(df: pd.DataFrame, entity_name_col: str, entity_content_col: str) -> pd.DataFrame:
    entity_df: pd.DataFrame = df[[entity_name_col, entity_content_col]]
    entity_df.drop_duplicates(inplace=True)
    entity_df.rename(
        columns={entity_name_col: "name", entity_content_col: "content"},
        inplace=True,
    )
    return entity_df


def split_df(
    df: pd.DataFrame,
    entity_1_name_col: str,
    entity_1_content_col: str,
    entity_1_label: str,
    entity_2_name_col: str,
    entity_2_content_col: str,
    entity_2_label: str,
    prefix: str,
):
    df_path = os.path.join(PREPARED_DATA_PATH, prefix)
    os.makedirs(
        df_path,
        exist_ok=True,
    )

    entity_1_df = get_entity_df(df, entity_1_name_col, entity_1_content_col)
    entity_1_fp = os.path.join(df_path, f"{entity_1_label}.csv")
    entity_1_df.to_csv(entity_1_fp, index=False)

    entity_2_df = get_entity_df(df, entity_2_name_col, entity_2_content_col)
    entity_2_fp = os.path.join(df_path, f"{entity_2_label}.csv")
    entity_2_df.to_csv(entity_2_fp, index=False)


if __name__ == "__main__":
    antibody_target = pd.read_csv(
        "data/reparsing/аня_парсинг/new_antibody_interactions.csv",
        index_col="Unnamed: 0",
    )
    antibody_target.drop_duplicates(inplace=True)
    split_df(
        antibody_target,
        entity_1_name_col="antibody_name",
        entity_1_content_col="antibody_sequence",
        entity_1_label="antibody",
        entity_2_name_col="target_name",
        entity_2_content_col="target_seq",
        entity_2_label="protein",
        prefix="new_antibody"
    )
    antibody_target.to_csv(os.path.join(PREPARED_DATA_PATH, "new_antibody", "new_antibody_interactions.csv"), index=False)

    dna_aptamers_mol_target = pd.read_csv(
        "data/reparsing/aptamers_interactions/new_aptamers_dna_mol_interactions.csv",
        index_col="Unnamed: 0",
    )
    split_df(
        dna_aptamers_mol_target,
        entity_1_name_col="apt_name",
        entity_1_content_col="apt_seq",
        entity_1_label="dna",
        entity_2_name_col="target_name",
        entity_2_content_col="target_seq",
        entity_2_label="small_molecule",
        prefix="new_aptamers_dna_mol"
    )
    dna_aptamers_mol_target.to_csv(os.path.join(PREPARED_DATA_PATH, "new_aptamers_dna_mol", "new_aptamers_interactions.csv"), index=False)

    rna_aptamers_mol_target = pd.read_csv(
        "data/reparsing/aptamers_interactions/new_aptamers_rna_mol_interactions.csv",
        index_col="Unnamed: 0",
    )
    split_df(
        rna_aptamers_mol_target,
        entity_1_name_col="apt_name",
        entity_1_content_col="apt_seq",
        entity_1_label="rna",
        entity_2_name_col="target_name",
        entity_2_content_col="target_seq",
        entity_2_label="small_molecule",
        prefix="new_aptamers_rna_mol"
    )
    rna_aptamers_mol_target.to_csv(os.path.join(PREPARED_DATA_PATH, "new_aptamers_rna_mol", "new_aptamers_interactions.csv"), index=False)

    dna_aptamers_protein_target = pd.read_csv(
        "data/reparsing/aptamers_interactions/new_aptamers_dna_protein_interactions.csv",
        index_col="Unnamed: 0",
    )
    split_df(
        dna_aptamers_protein_target,
        entity_1_name_col="apt_name",
        entity_1_content_col="apt_seq",
        entity_1_label="dna",
        entity_2_name_col="target_name",
        entity_2_content_col="target_seq",
        entity_2_label="protein",
        prefix="new_aptamers_dna_protein"
    )
    dna_aptamers_protein_target.to_csv(os.path.join(PREPARED_DATA_PATH, "new_aptamers_dna_protein", "new_aptamers_interactions.csv"), index=False)

    rna_aptamers_protein_target = pd.read_csv(
        "data/reparsing/aptamers_interactions/new_aptamers_rna_protein_interactions.csv",
        index_col="Unnamed: 0",
    )
    split_df(
        rna_aptamers_protein_target,
        entity_1_name_col="apt_name",
        entity_1_content_col="apt_seq",
        entity_1_label="rna",
        entity_2_name_col="target_name",
        entity_2_content_col="target_seq",
        entity_2_label="protein",
        prefix="new_aptamers_rna_protein"
    )
    rna_aptamers_protein_target.to_csv(os.path.join(PREPARED_DATA_PATH, "new_aptamers_rna_protein", "new_aptamers_interactions.csv"), index=False)

    repeats_df = pd.read_csv(
        "data/reparsing/иван_парсинг/Repeats_annotation.csv",
        index_col="Unnamed: 0",
    )
    ribosomal_df = pd.read_csv(
        "data/reparsing/иван_парсинг/Ribosomal_annotation.csv",
        index_col="Unnamed: 0",
    )
    riboswitrch_df = pd.read_csv(
        "data/reparsing/иван_парсинг/Riboswitch_annotation.csv",
        index_col="Unnamed: 0",
    )
    viral_df = pd.read_csv(
        "data/reparsing/иван_парсинг/Viral_annotation.csv",
        index_col="Unnamed: 0",
    )
    miRNA_df = pd.read_csv(
        "data/reparsing/иван_парсинг/miRNA_annotation.csv",
        index_col="Unnamed: 0",
    )
    aptamer_df = pd.concat([repeats_df, ribosomal_df, riboswitrch_df, viral_df, miRNA_df], axis=0)
    aptamer_df.drop_duplicates(inplace=True)
    split_df(
        aptamer_df,
        entity_1_name_col="RNA_name",
        entity_1_content_col="rna_content",
        entity_1_label="aptamer",
        entity_2_name_col="small_molecule_name",
        entity_2_content_col="small_molecule_content",
        entity_2_label="small_molecule",
        prefix="aptamer_datasets"
    )
    aptamer_df.to_csv(os.path.join(PREPARED_DATA_PATH, "aptamer_datasets", "aptamers_annotation.csv"), index=False)
