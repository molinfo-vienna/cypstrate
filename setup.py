from setuptools import find_packages, setup

# some RDKit versions are not recognized by setuptools
# -> check if RDKit is installed by attempting to import it
# -> if RDKit can be imported, do not add it to install_requires
rdkit = False
try:
    from rdkit import Chem

    rdkit = True
except ImportError:
    pass

# rdkit 2022.3.3 is the oldest (reasonable) version
rdkit_requirement = ["rdkit>=2022.3.3"] if not rdkit else []

setup(
    name="cypstrate",
    version="0.1",
    maintainer="Johannes Kirchmair",
    maintainer_email="johannes.kirchmair@univie.ac.at",
    packages=find_packages(),
    url="https://github.com/molinfo-vienna/cypstrate.git",
    description="CYPstrate: Prediction of Cytochrome P450 substrates",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=rdkit_requirement
    + [
        "scikit-learn==0.23.2",
        "gensim==3.8.3",
        "pandas==1.2.1",
        "numpy==1.19.2",
        "nerdd-module>=0.1.0",
        "mol2vec @ git+https://github.com/samoturk/mol2vec",
        "acm-hamburg-legacy @ git+https://github.com/molinfo-vienna/acm-hamburg-legacy.git",
        # chembl_structure_pipeline 1.0.0 is not on PyPI
        "chembl_structure_pipeline @ git+https://github.com/chembl/ChEMBL_Structure_Pipeline.git@1.0.0",
        # avoid warnings about numpy.distutils
        "setuptools < 60.0",
    ],
    extras_require={
        "dev": [
            "mypy",
            "isort",
            "black",
        ],
        "test": [
            "pytest",
            "pytest-watch",
            "pytest-cov",
            "pytest-bdd",
            "hypothesis",
            "hypothesis-rdkit",
        ],
    },
    entry_points={
        "console_scripts": [
            "cypstrate=cypstrate.__main__:main",
        ],
    },
)
