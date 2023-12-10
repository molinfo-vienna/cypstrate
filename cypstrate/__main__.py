from nerdd_module import auto_cli

from .cypstrate_model import CypstrateModel


@auto_cli
def main():
    return CypstrateModel()
