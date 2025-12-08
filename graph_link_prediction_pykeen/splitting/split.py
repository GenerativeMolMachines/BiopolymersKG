from pykeen.triples import TriplesFactory

def split_data(path: str, ratios: list[float] = [.8, .1, .1], random_state: int = None):

    triples = TriplesFactory.from_path(
        path=path,
        create_inverse_triples=False,
        load_triples_kwargs=dict(delimiter=",")
    )

    print(triples.num_triples)

    train, test, val = triples.split(ratios=ratios, random_state=random_state)

    print(train.num_triples)
    print(test.num_triples)
    print(val.num_triples)

    return train, test, val