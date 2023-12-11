# Cypstrate

CYPstrate consists of a collection of machine learning classifiers (random forest and
support vector machines) for the prediction of substrates and non-substrates of the nine
most important human CYP isozymes in the metabolism of xenobiotics (i.e. CYPs 1A2, 2A6,
2B6, 2C8, 2C9, 2C19, 2D6, 2E1 and 3A4). The models are trained on a high-quality data
set of 1831 substrates and non-substrates compiled from public sources.

## Installation

```bash
# requires Python 3.8
pip install -U cypstrate
```

## Usage

CYPstrate can be called from the **command line**. Examples:

```bash
# input in SMILES format
cypstrate "CCOC(=O)N1CCN(CC1)C2=C(C(=O)C2=O)N3CCN(CC3)C4=CC=C(C=C4)OC"

# prediction is one of "best_performance" (default) or "full_coverage"
cypstrate --prediction-mode full_coverage "CCN(C)C(=O)OC1=CC=CC(=C1)C(C)N(C)C"

# input can be a file
cypstrate molecules.sdf > result.csv

# output format can be specified
cypstrate --output sdf molecules.smiles > result.sdf

# more information via --help
cypstrate --help
```

The model can be used in **Python**. Calling the ```predict``` function of the 
```CypstrateModel``` class results in a pandas DataFrame containing the prediction 
results for each input molecule.

```python
from cypstrate import CypstrateModel

model = CypstrateModel()

# "predict" method accepts a list of SMILES representations
df_predictions = model.predict(['CCN(C)C(=O)OC1=CC=CC(=C1)C(C)N(C)C'])

# ... or a list of file paths
df_predictions = model.predict(['part1.sdf', 'part2.sdf'])
```

The result DataFrame contains the columns:
* **mol_id**: unique number identifying the input molecule
* **input**: the raw representation provided as input (e.g. OCCCCC)
* **input_type**: the representation type of the input (e.g. smiles)
* **source**: the input source (e.g. my_molecules.sdf)
* **name**: the name of the input molecule (if provided in the input)
* **input_mol**: the RDKit molecule parsed from the input representation
* **preprocessed_mol**: the RDKit molecule after preprocessing
* **errors**: a list of errors that occured during reading or preprocessing the input
* **prediction_1a2, prediction_2a6, prediction_2b6, prediction_2c8, prediction_2c9, 
prediction_2c19, prediction_2d6, prediction_2e1, prediction_3a4**: probability (between 
0 and 1) of being a substrate of the given CYP isozyme
* **neighbor_1a2, neighbor_2a6, neighbor_2b6, neighbor_2c8, neighbor_2c9, 
neighbor_2c19, neighbor_2d6,neighbor_2e1,neighbor_3a4**: similarity to the most similar 
molecule in the corresponding training set


## Contribute

```bash
conda env create -f environment.yml
conda activate cypstrate
pip install -e .[dev,test]
ptw
```


## Contributors

* Malte Holmer
* Steffen Hirte
* Axinya Tokareva
