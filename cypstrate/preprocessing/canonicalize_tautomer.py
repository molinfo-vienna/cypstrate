import logging
from typing import List, Tuple

# disable rdkit logging messages
# importing rdMolStandardize already logs messages
from rdkit import RDLogger

logger = RDLogger.logger()
logger.setLevel(RDLogger.ERROR)

from nerdd_module import Problem
from nerdd_module.preprocessing import PreprocessingStep
from rdkit.Chem import KekulizeException, Mol, SanitizeMol
from rdkit.Chem.MolStandardize import rdMolStandardize

__all__ = ["CanonicalizeTautomer"]


if hasattr(rdMolStandardize, "GetV1TautomerEnumerator"):
    TautomerEnumerator = rdMolStandardize.GetV1TautomerEnumerator
else:
    TautomerEnumerator = rdMolStandardize.TautomerEnumerator


class CanonicalizeTautomer(PreprocessingStep):
    """Canonalizes the molecules by removing stereochemistry and
    enumerating tautomers.
    """

    def __init__(self, remove_stereo=False, remove_invalid_molecules=False):
        super().__init__()
        self.remove_stereo = remove_stereo
        self.remove_invalid_molecules = remove_invalid_molecules

    def _preprocess(self, mol: Mol) -> Tuple[Mol, List[Problem]]:
        problems: List[Problem] = []

        # generating a canonical tautomer might ignore stereochemistry
        canon = TautomerEnumerator()
        if not self.remove_stereo:
            canon.SetRemoveBondStereo(False)
            canon.SetRemoveSp3Stereo(False)

        SanitizeMol(mol)
        try:
            # avoid tautomer enumeration warnings
            logger.setLevel(RDLogger.ERROR)
            molc = canon.Canonicalize(mol)
            logger.setLevel(RDLogger.WARNING)

            if molc is None:
                raise KekulizeException()
            return molc, problems
        except KekulizeException:
            problems.append(
                Problem(
                    "canonicalization_failed", "Canonicalizing the molecule failed."
                )
            )
            if self.remove_invalid_molecules:
                return None, problems
            else:
                return mol, problems
