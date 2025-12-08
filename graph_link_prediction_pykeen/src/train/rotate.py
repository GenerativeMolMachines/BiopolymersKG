import pandas as pd
from pykeen.triples import TriplesFactory
from pykeen.models import RotatE
from pykeen.training import SLCWATrainingLoop
from pykeen.losses import MarginRankingLoss
from pykeen.evaluation import RankBasedEvaluator
from pykeen.optimizers import Adam
from pykeen.regularizers import LpRegularizer
import optuna
import json


LR = 1e-3
EPOCHS = 50
WEIGHT = 1e-3
device = 'cuda'
batch_size = 4096

df_sparse = pd.read_csv("/mnt/tank/scratch/pbogdanov/link_pykeen/data/data_for_training/iw_hs/iw_hs.csv")

main_data = df_sparse.astype(str)

triples = main_data[["entity_1", "predicate", "entity_2"]].values
triplet_data = TriplesFactory.from_labeled_triples(triples, create_inverse_triples=False)
training_set, testing_set, validation_set = triplet_data.split([0.8, 0.1, 0.1], random_state=100)

def objective(trial):
    embedding_dim = trial.suggest_int("embedding_dim", 128, 848)
    margin = trial.suggest_float("margin", 1, 5)
    # batch_size = trial.suggest_int("batch_size", 2500, 5000)
    num_negs = trial.suggest_int("num_negs_per_pos", 1, 10)
    
    loss_function = MarginRankingLoss(margin=margin)
    model = RotatE(
        triples_factory=training_set,
        embedding_dim=embedding_dim,
        random_seed=100,
        loss = loss_function,
        regularizer=LpRegularizer,
        regularizer_kwargs=dict(p=2, weight=WEIGHT),
    )
    model = model.to(device)
    
    optimizer = Adam(params=model.get_grad_params(), lr=LR)
    
    training_loop = SLCWATrainingLoop(
        model=model,
        triples_factory=training_set,
        optimizer=optimizer,
        negative_sampler='pseudotyped',
        negative_sampler_kwargs=dict(
            num_negs_per_pos=num_negs
        )
    )
    
    evaluator = RankBasedEvaluator()
    
    training_loop.train(
        num_epochs=EPOCHS,
        batch_size=batch_size,
        triples_factory=training_set,
        use_tqdm_batch=False,
    )
    
    model_results = evaluator.evaluate(
        model=model,
        mapped_triples=testing_set.mapped_triples.to(device),
        additional_filter_triples=[
                training_set.mapped_triples.to(device),
                validation_set.mapped_triples.to(device),
            ],
    )

    metrics = model_results.to_df()
    metrics = metrics[(metrics['Side'] == 'both') & (metrics['Rank_type'] == 'realistic') & (metrics['Metric'] == 'inverse_harmonic_mean_rank')]
    return metrics['Value'].item()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=28)

print("Best hyperparameters: ", study.best_params)
print("Best MRR: ", study.best_value)

with open("/mnt/tank/scratch/pbogdanov/link_pykeen/results/rotate_iw_hs_hyperparameters.json", "w") as f:
    json.dump(study.best_params, f, indent=4)