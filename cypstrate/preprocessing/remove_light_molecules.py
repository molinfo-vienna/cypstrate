from typing import List, Tuple

from nerdd_module import Problem
from nerdd_module.preprocessing import PreprocessingStep
from rdkit.Chem import Mol


class RemoveLightMolecules(PreprocessingStep):
    def __init__(self):
        super().__init__()

    def _preprocess(self, mol: Mol) -> Tuple[Mol, List[Problem]]:
        errors = []

        try:
            if mol.GetNumHeavyAtoms() == 0:
                mol = None
                errors.append(
                    Problem(
                        "no_heavy_atoms",
                        "The molecule contains no heavy atoms.",
                    )
                )
        except:
            mol = None
            errors.append(Problem("invalid_input", "The molecule is invalid."))

        return mol, errors
