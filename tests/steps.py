from pytest_bdd import given, parsers, when

from cypstrate import CypstrateModel


@given(
    parsers.parse("the prediction mode is '{prediction_mode}'"),
    target_fixture="prediction_mode",
)
def cypstrate_prediction_mode(prediction_mode):
    return prediction_mode


@when(
    parsers.parse("the cypstrate model generates predictions for the molecule representations"),
    target_fixture="predictions",
)
def predictions(representations, prediction_mode):
    model = CypstrateModel()
    return model.predict(
        representations,
        prediction_mode=prediction_mode,
        output_format="record_list",
    )
