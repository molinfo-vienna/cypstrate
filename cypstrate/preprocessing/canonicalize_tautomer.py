import logging
from typing import List, Tuple

# disable rdkit logging messages
# importing rdMolStandardize already logs messages
from rdkit import RDLogger

logger = RDLogger.logger()
logger.setLevel(RDLogger.ERROR)

from nerdd_module.preprocessing import Step
from rdkit.Chem import KekulizeException, Mol, SanitizeMol
from rdkit.Chem.MolStandardize import rdMolStandardize

__all__ = ["CanonicalizeTautomer"]


class CanonicalizeTautomer(Step):
    """Canonalizes the molecules by removing stereochemistry and
    enumerating tautomers.
    """

    def __init__(self, remove_stereo=False, remove_invalid_molecules=False):
        super().__init__()
        self.remove_stereo = remove_stereo
        self.remove_invalid_molecules = remove_invalid_molecules

    def _run(self, mol: Mol) -> Tuple[Mol, List[str]]:
        errors = []

        # generating a canonical tautomer might ignore stereochemistry
        canon = rdMolStandardize.GetV1TautomerEnumerator()
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
            return molc, errors
        except KekulizeException:
            errors.append("C1")
            if self.remove_invalid_molecules:
                return None, errors
            else:
                return mol, errors
