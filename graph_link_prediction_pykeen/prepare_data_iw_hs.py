import pandas as pd
from pathlib import Path
from pykeen.triples import TriplesFactory

ROW_DIR = Path("data/raw_data/export_iw_hs")
CLEAN_DIR = Path("data/data_for_training/iw_hs")
CLEAN_DIR.mkdir(exist_ok=True, parents=True)

USE_COLS = ["entity_1", "predicate", "entity_2"]

csv_files = sorted(ROW_DIR.glob("export_part_*.csv"))

dfs = []
for file in csv_files:
    df = pd.read_csv(file, usecols=USE_COLS)
    dfs.append(df)

all_data = pd.concat(dfs, ignore_index=True)
all_data = all_data.sample(frac=1, random_state=42)

all_data["entity_1"] = all_data["entity_1"].astype(str).str.strip()
all_data["entity_2"] = all_data["entity_2"].astype(str).str.strip()
all_data["predicate"] = all_data["predicate"].astype(str).str.strip()

all_data.to_csv(CLEAN_DIR / "iw_hs.csv", index=False)

# all_data_iw = all_data[all_data["predicate"] == 'interacts_with']
# all_data_hs = all_data[all_data["predicate"] == 'has_similarity']

# tf_iw = TriplesFactory.from_labeled_triples(
#     all_data_iw[["entity_1", "predicate", "entity_2"]].to_numpy(),
#     create_inverse_triples=False
# )

# train_iw, test_iw, val_iw = tf_iw.split(
#     ratios=[0.8, 0.1, 0.1],
#     random_state=42,
# )

# tf_hs = TriplesFactory.from_labeled_triples(
#     all_data_hs[["entity_1", "predicate", "entity_2"]].to_numpy(),
#     create_inverse_triples=False
# )

# # Преобразуем IW-train обратно в текстовые triple (head, rel, tail)
# df_train_iw = pd.DataFrame(
#     train_iw.triples,
#     columns=["entity_1", "predicate", "entity_2"]
# )

# # Объединяем IW-train и SIM
# df_train_all = pd.concat(
#     [df_train_iw, all_data_hs],
#     ignore_index=True
# )

# # Создаём финальный train TriplesFactory
# train_final = TriplesFactory.from_labeled_triples(
#     df_train_all[["entity_1", "predicate", "entity_2"]].to_numpy(),
#     create_inverse_triples=False
# )


# print("Train final triples:", train_final.num_triples)
# print("Test IW triples:", test_iw.num_triples)
# print("Val IW triples:", val_iw.num_triples)

# df_train_final = pd.DataFrame(
#     train_final.triples,
#     columns=["entity_1", "predicate", "entity_2"]
# )

# df_test_iw = pd.DataFrame(
#     test_iw.triples,
#     columns=["entity_1", "predicate", "entity_2"]
# )

# df_val_iw = pd.DataFrame(
#     val_iw.triples,
#     columns=["entity_1", "predicate", "entity_2"]
# )

# df_train_final.to_csv(CLEAN_DIR / "iw_hs.csv", index=False)
# df_test_iw.to_csv(CLEAN_DIR / "iw_hs_val.csv", index=False)
# df_val_iw.to_csv(CLEAN_DIR / "iw_hs_test.csv", index=False)
