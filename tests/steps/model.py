from pytest_bdd import given, parsers

from cypstrate import CypstrateModel


@given("the CYPstrate model", target_fixture="model")
def model():
    return CypstrateModel()


@given(parsers.parse("the input type is '{input_type}'"), target_fixture="input_type")
def input_type(input_type):
    return input_type


@given(
    parsers.parse("the prediction mode is '{prediction_mode}'"),
    target_fixture="prediction_mode",
)
def prediction_mode(prediction_mode):
    return prediction_mode
