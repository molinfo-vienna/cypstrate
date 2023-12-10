import warnings
from functools import partial
from itertools import product
from multiprocessing import Pool
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# avoid warnings from word2vec
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from gensim.models import word2vec

from .preprocessing import CypstratePreprocessingPipeline

try:
    # works in python 3.9+
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from joblib import load
from mol2vec import features as m2v_features
from nerdd_module import AbstractModel
from rdkit.Chem import AllChem, DataStructs, Descriptors, Mol
from rdkit.Chem.GraphDescriptors import Ipc
from rdkit.ML.Descriptors import MoleculeDescriptors
from scipy.spatial.distance import cdist

__all__ = ["CypstrateModel"]

current_dir = files("cypstrate")
models_path = current_dir / "models"
fps_path = current_dir / "maccs_fps"
feature_sets = ["rdkit", "morg2", "maccs", "mol2vec"]
prediction_modes = ["best_performance", "full_coverage"]

cyp_model_input_dict: Dict[str, Dict[str, Tuple]] = {}
for pred_mode in prediction_modes:
    cyp_model_input_dict[pred_mode] = {}
    model_pred_path = models_path / pred_mode

    for model_path in model_pred_path.iterdir():
        model_name = model_path.name
        cyp = model_name.split("_")[1].lower()
        input_feature_sets = list(
            filter(lambda f_set: f_set in model_name, feature_sets)
        )

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            model = load(model_pred_path / model_name)

        cyp_model_input_dict[pred_mode][cyp] = (model, input_feature_sets)

trainset_fps = {}
for fp_path in fps_path.iterdir():
    fp_name = fp_path.name
    cyp = fp_name.split("_")[3].split(".")[0].lower()
    trainset_fps[cyp] = np.load(
        (fps_path / f"maccs_fps_trainset_{cyp.upper()}.npy").open("rb")
    )

descriptor_file = models_path / "rdkit_descriptors_used.txt"
with descriptor_file.open("r") as desc_file:
    descriptors_used = desc_file.read().split("\t")


m2v_model = word2vec.Word2Vec.load(str(models_path / "model_300dim_mol2vec.pkl"))


def chunk_list_into_n_lists(l, n):
    """
    method to chunk a list for multiprocessing

    :param l: any kind of list
    :param n: number of chunks to chunk the list into
    :return: list (with len(n)) of equally distributed lists
    """
    c = int(len(l) / n)
    if c == 0:
        c = 1
    return [l[x : x + c] for x in range(0, len(l), c)]


def get_maccs_keys(mol):
    """
    Method to calculate MACCS keys

    :param mol rdkit molecule
    :return: np.array with MACCS keys
    """
    maccs_key = np.empty(167)
    DataStructs.ConvertToNumpyArray(AllChem.GetMACCSKeysFingerprint(mol), maccs_key)

    return maccs_key[1:]


def get_mol2vec(mols, model):
    """
    Method to calculate mol2vec vectors

    :param mols rdkit molecules
    :return: array with mol2vec vectors
    """
    sentences = [m2v_features.mol2alt_sentence(mol, radius=1) for mol in mols]
    m2v_vecs = m2v_features.sentences2vec(
        sentences=sentences, model=model, unseen="UNK"
    )

    return m2v_vecs


def get_morgan2_fp(mol):
    """
    Method to calculate MACCS keys

    :param mol rdkit molecule
    :return: np.array with a morgan2 fingerprint
    """
    morgan2_fp = np.empty(2048)
    DataStructs.ConvertToNumpyArray(
        AllChem.GetMorganFingerprintAsBitVect(mol, 2, 2048), morgan2_fp
    )

    return morgan2_fp


def get_rdkit(mols):
    """
    Method to calculate rdkit descriptors

    :param mols rdkit molecules
    :return: list with rdkit descriptors for several mols
    """
    Descriptors.Ipc = partial(Ipc, avg=1)

    calculator = MoleculeDescriptors.MolecularDescriptorCalculator(descriptors_used)

    rdkit_2d_descs = []
    for mol in mols:
        value = np.array(calculator.CalcDescriptors(mol), dtype="float32")
        value[~np.isfinite(value)] = 10000
        rdkit_2d_descs.append(value)

    return rdkit_2d_descs


def get_prediction(model, X):
    return model.predict(X)


def map_results_to_readable_output(results):
    """
    maps the list of results to readable output without changing the array buildup

    :param results: list of lists
    :return: list of lists with readable results entries
    """
    for i in range(len(results)):
        for j in range(len(results[0])):
            entry = results[i][j]
            if np.isnan(entry):
                results[i][j] = "No prediction"
            elif entry == 0:
                results[i][j] = "Non-substrate"
            elif entry == 1:
                results[i][j] = "Substrate"
    return results


def get_molsim_for_cyp(mol_fps, cyp):
    """
    Method to calculate the nearest neighbor molecular similarity as tanimoto coefficient to the training set
    that was used to train the specified CYP model.

    :param mols rdkit molecules
    :param cyp the cyp substrate for which the molecular similarity to the training set should be calculated
    :parm path to the location of the fp matrices for the training sets

    :return array with nearest neighbor molecular similarities (as TC) for one cyp
    """
    return nearest_neighbor_fps_to_fps(mol_fps, trainset_fps[cyp])


def nearest_neighbor_fps_to_fps(target_fps, ref_fps):
    """
    Calculates the tanimoto coefficient to the nearest neighbor based on fingerprints.
    Both inputs are provided as 2-d numpy arrays with vectors that contain all bits of a fingerprint.

    :param target_fps 2d numpy array with fingerprints for which the nearest neighbor molecular similarity to the other matrix should be calculated
    :param ref_fps 2d numpy array that has fps for the molecules in the reference data set (here it is the training set)

    :return array with the nearest neighbor similarity
    """
    tani_sims = 1 - cdist(target_fps, ref_fps, metric="jaccard")

    nearest_neighbor_sims = tani_sims.max(axis=1).round(decimals=2)

    return nearest_neighbor_sims


def predict(
    mols: List[Mol],
    prediction_mode: str = "best_performance",
    applicability_domain: bool = True,
):
    cyps = ["1a2", "2a6", "2b6", "2c8", "2c9", "2c19", "2d6", "2e1", "3a4"]

    if len(mols) == 0:
        columns = [f"prediction_{cyp}" for cyp in cyps] + [
            f"neighbor_{cyp}" for cyp in cyps
        ]
        return pd.DataFrame(columns=columns)

    cores = 4

    # calculate features
    desc_dict = {}

    pool = Pool(cores)

    # # Prepare descriptors
    desc_dict["morg2"] = np.vstack(pool.map(get_morgan2_fp, mols))
    desc_dict["maccs"] = np.vstack(pool.map(get_maccs_keys, mols))

    mols_init = mols
    mols = chunk_list_into_n_lists(mols, cores)

    # Mol2Vec calculation
    get_mol2vec_partial = partial(get_mol2vec, model=m2v_model)

    # mol2vec = np.vstack([get_mol2vec_partial(m) for m in mols])
    desc_dict["mol2vec"] = np.vstack(pool.map(get_mol2vec_partial, mols))

    # rdkit calculation
    desc_dict["rdkit"] = np.vstack(pool.map(get_rdkit, mols))

    # calculate similarity to training data
    if applicability_domain:
        star_inputs = product([desc_dict["maccs"]], cyps)
        # ads_per_cyp
        nnm_predictions = np.array(pool.starmap(get_molsim_for_cyp, star_inputs))
    else:
        nnm_predictions = np.ones((len(cyps), len(mols_init))) * -1

    # machine learning prediction
    input_pairs_ml = []

    for cyp in cyps:
        model, inputs = cyp_model_input_dict[prediction_mode][cyp]
        X = np.hstack([desc_dict[input] for input in inputs])
        pair = (model, X)
        input_pairs_ml.append(pair)

    results = pool.starmap(get_prediction, input_pairs_ml)
    results = [list(r) for r in results]

    mlm_predictions = np.array(map_results_to_readable_output(results))

    pool.terminate()

    final_results = dict()
    for i, label in enumerate(cyps):
        final_results[f"prediction_{label}"] = mlm_predictions[i, :]
        final_results[f"neighbor_{label}"] = nnm_predictions[i, :]

    return pd.DataFrame(final_results)


class CypstrateModel(AbstractModel):
    def __init__(self):
        super().__init__(preprocessing_pipeline=CypstratePreprocessingPipeline())

    def _predict_mols(
        self,
        mols: List[Mol],
        prediction_mode: str = "best_performance",
        applicability_domain: bool = True,
    ):
        assert prediction_mode is not None

        prediction_mode = prediction_mode.lower()
        assert prediction_mode in prediction_modes

        return predict(mols, prediction_mode, applicability_domain)
