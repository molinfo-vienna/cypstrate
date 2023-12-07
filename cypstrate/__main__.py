from nerdd_module.cli import auto_cli

from .cypstrate_model import CypstrateModel


@auto_cli
def main():
    return CypstrateModel()
