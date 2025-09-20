from nerdd_module.preprocessing import (
    FilterByElement,
    FilterByWeight,
    GetParentMolWithCsp,
    StandardizeWithCsp,
)

from .canonicalize_tautomer import CanonicalizeTautomer
from .do_smiles_roundtrip import DoSmilesRoundtrip

__all__ = ["cypstrate_preprocessing_steps"]


cypstrate_preprocessing_steps = [
    DoSmilesRoundtrip(remove_stereo=True),
    StandardizeWithCsp(),
    GetParentMolWithCsp(),
    FilterByWeight(
        min_weight=0,
        max_weight=10_000,
        remove_invalid_molecules=True,
    ),
    FilterByElement(
        allowed_elements=[
            "H",
            "B",
            "C",
            "N",
            "O",
            "F",
            "Si",
            "P",
            "S",
            "Cl",
            "Se",
            "Br",
            "I",
        ],
        remove_invalid_molecules=True,
    ),
    CanonicalizeTautomer(
        remove_stereo=True,
        remove_invalid_molecules=True,
    ),
    DoSmilesRoundtrip(remove_stereo=False),
]
