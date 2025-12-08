from omegaconf import OmegaConf
import sys


def get_torchbiggraph_config():
    cfg = OmegaConf.load("params.yaml")

    # Process relations - ensure it's always a list
    if OmegaConf.is_list(cfg.relations):
        relations_list = [OmegaConf.to_container(rel, resolve=True) for rel in cfg.relations]
    else:
        relations_list = [OmegaConf.to_container(cfg.relations, resolve=True)]
    
    # Debug output
    print(f"[DEBUG] Number of relations: {len(relations_list)}", file=sys.stderr)
    for i, rel in enumerate(relations_list):
        print(f"[DEBUG] Relation {i}: {rel.get('name', 'NO_NAME')}", file=sys.stderr)

    config = dict(
        #I/O
        entity_path=cfg.entity_path,
        edge_paths=[
            cfg.edge_paths.train,
            cfg.edge_paths.test,
            cfg.edge_paths.val,
        ],
        #Graph structure
        entities=OmegaConf.to_container(cfg.entities, resolve=True),
        relations=relations_list,
        workers=cfg.import_data.workers,
    )

    return config
