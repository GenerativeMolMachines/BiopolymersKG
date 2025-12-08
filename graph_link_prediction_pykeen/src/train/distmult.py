import pandas as pd
import random
import torch
import numpy as np
from pathlib import Path
from pykeen.triples import TriplesFactory
from pykeen.pipeline import pipeline
from pykeen.hpo import hpo_pipeline
import networkx as nx
import numpy as np
import pandas as pd
import optuna
import matplotlib.pyplot as plt



device = "cuda" if torch.cuda.is_available() else "cpu"
print("Используем устройство:", device)


df_sparse = pd.read_csv("/mnt/tank/scratch/pbogdanov/link_pykeen/data/data_for_training/iw/iw.csv")

triples = df_sparse[["entity_1", "predicate", "entity_2"]].astype(str).to_numpy()

tf = TriplesFactory.from_labeled_triples(triples)

train, val, test = tf.split([.8, .1, .1], random_state=42)

result_distmult = pipeline(
    training=train,
    validation=val,
    testing=test,
    model="DistMult",
    model_kwargs=dict(
        embedding_dim=128,
    ),
    loss="MarginRankingLoss",
    loss_kwargs=dict(
        margin=1.0
    ),
    negative_sampler="bernoulli",
    negative_sampler_kwargs=dict(num_negs_per_pos=1),
    training_loop="sLCWA",
    training_kwargs=dict(
        num_epochs=3,
        batch_size=512,
    ),
    optimizer="adagrad",
    optimizer_kwargs=dict(lr=0.01),
    random_seed=42,
    device=device
)

m_distmult = result_distmult.metric_results.to_dict()


import json

mrr_distmult = m_distmult["both"]["realistic"]["inverse_harmonic_mean_rank"]
hits1_distmult = m_distmult["both"]["realistic"]["hits_at_1"]
hits3_distmult = m_distmult["both"]["realistic"]["hits_at_3"]
hits10_distmult = m_distmult["both"]["realistic"]["hits_at_10"]

metrics = {
    "mrr": float(mrr_distmult),
    "hits@1": float(hits1_distmult),
    "hits@3": float(hits3_distmult),
    "hits@10": float(hits10_distmult)
}

with open("/mnt/tank/scratch/pbogdanov/link_pykeen/results/distmult_iw_metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)


def objective(trial):
    embedding_dim = trial.suggest_int("embedding_dim", 32, 256)
    margin = trial.suggest_float("margin", 1, 10)
    batch_size = trial.suggest_int("batch_size", 128, 1024)
    lr = trial.suggest_float("lr", 0.001, 0.1, log=True)
    num_negs = trial.suggest_int("num_negs_per_pos", 1, 10)

    result_distmult = pipeline(
        training=train,
        validation=val,
        testing=test,

        model="DistMult",
        model_kwargs=dict(
            embedding_dim=embedding_dim,
        ),

        loss="MarginRankingLoss",
        loss_kwargs=dict(
            margin=margin,
        ),
        negative_sampler="bernoulli",
        negative_sampler_kwargs=dict(num_negs_per_pos=num_negs),
        
        training_loop="sLCWA",
        training_kwargs=dict(
            num_epochs=100,
            batch_size=batch_size
        ),

        optimizer="adagrad",
        optimizer_kwargs=dict(lr=lr),
        random_seed=42,
        device=device
    )

    mrr = result_distmult.get_metric("mrr")
    trial.report(mrr, step=0)

    return mrr

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=25)

print("Best hyperparameters: ", study.best_params)
print("Best MRR: ", study.best_value)



final_result = pipeline(
    training=train,
    testing=test,        
    model="DistMult",
    model_kwargs=dict(
        embedding_dim=study.best_params['embedding_dim'],
    ),
    loss="MarginRankingLoss",
    loss_kwargs=dict(margin=study.best_params['margin']),
    negative_sampler="bernoulli",
    negative_sampler_kwargs=dict(
        num_negs_per_pos=study.best_params['num_negs_per_pos'],
    ),
    training_loop="sLCWA",
    training_kwargs=dict(
        num_epochs=100,                    
        batch_size=study.best_params['batch_size'],
    ),
    optimizer="adagrad",
    optimizer_kwargs=dict(lr=study.best_params['lr']),
    random_seed=42,
    device=device,
)


m_distmult_opt = result_distmult.metric_results.to_dict()


mrr_distmult_opt = m_distmult_opt["both"]["realistic"]["inverse_harmonic_mean_rank"]
hits1_distmult_opt = m_distmult_opt["both"]["realistic"]["hits_at_1"]
hits3_distmult_opt = m_distmult_opt["both"]["realistic"]["hits_at_3"]
hits10_distmult_opt = m_distmult_opt["both"]["realistic"]["hits_at_10"]

metrics_opt = {
    "mrr": float(mrr_distmult_opt),
    "hits@1": float(hits1_distmult_opt),
    "hits@3": float(hits3_distmult_opt),
    "hits@10": float(hits10_distmult_opt)
}

with open("/mnt/tank/scratch/pbogdanov/link_pykeen/results/distmult_iw_metrics_opt.json", "w") as f:
    json.dump(metrics_opt, f, indent=4)


