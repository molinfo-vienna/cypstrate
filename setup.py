from setuptools import find_packages, setup

setup(
    name="cypstrate",
    version="0.2.3",
    maintainer="Johannes Kirchmair",
    maintainer_email="johannes.kirchmair@univie.ac.at",
    packages=find_packages(),
    python_requires=">=3.9,<3.10",
    url="https://github.com/molinfo-vienna/cypstrate.git",
    description="CYPstrate: Prediction of Cytochrome P450 substrates",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="BSD 3-Clause License",
    include_package_data=True,
    install_requires=[
        "rdkit==2020.09.1",
        "scikit-learn==0.23.2",
        "gensim==3.8.3",
        "numpy==1.20.3",
        "mol2vec==0.2.2",
        "nerdd-module>=0.3.16",
        "chembl_structure_pipeline==1.0.0",
        # avoid warnings about numpy.distutils
        "setuptools < 60.0",
        # install importlib-resources and importlib-metadata for old Python versions
        "importlib-resources>=5; python_version<'3.9'",
        "importlib-metadata>=4.6; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "mypy",
            "ruff",
        ],
        "test": [
            "pytest",
            "pytest-watch",
            "pytest-cov",
            "pytest-bdd==7.3.0",
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
