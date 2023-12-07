import numpy as np
import pandas as pd
from hypothesis import given as hgiven
from hypothesis import note, seed, settings
from hypothesis import strategies as st
from hypothesis.strategies import lists, none, one_of
from hypothesis_rdkit import mols, smiles
from pytest_bdd import given, parsers, scenario, then, when
from rdkit.Chem import MolFromSmiles, MolToMolBlock, MolToSmiles

cyps = ["1a2", "2a6", "2b6", "2c8", "2c9", "2c19", "2d6", "2e1", "3a4"]


@scenario(
    "features/valid_predictions.feature",
    "Predictions are valid",
)
def test_valid_predictions():
    pass


@given(parsers.parse("a random seed set to {seed:d}"), target_fixture="random_seed")
def random_seed(seed):
    return seed


@given(
    parsers.parse(
        "a list of {num:d} random molecules, where {num_none:d} entries are None"
    ),
    target_fixture="molecules",
)
def molecules(num, num_none, random_seed):
    result = None

    # pytest-bdd and hypothesis don't play well together (yet)
    # --> use this workaround to generate random molecules
    @hgiven(st.lists(smiles(), min_size=num, max_size=num, unique=True))
    @settings(max_examples=1, deadline=None)
    @seed(random_seed)
    def generate(smiles):
        nonlocal result
        result = [MolFromSmiles(s) for s in smiles]

    generate()

    # replace random entries with None
    indices = np.random.choice(num, num_none, replace=False)
    for i in indices:
        result[i] = None

    return result


@given(
    parsers.parse("the representations of the molecules"),
    target_fixture="representations",
)
def representations(molecules, input_type):
    if input_type == "smiles":
        converter = MolToSmiles
    elif input_type == "mol_block":
        converter = MolToMolBlock
    elif input_type == "rdkit_mol":
        converter = lambda mol: mol
    else:
        raise ValueError(f"Unknown input_type: {input_type}")

    result = [converter(mol) if mol is not None else None for mol in molecules]

    return result
