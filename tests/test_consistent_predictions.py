from pytest_bdd import given, parsers, scenario


@scenario(
    "features/consistent_predictions.feature",
    "Predictions stay consistent with previous versions",
)
def test_consistent_predictions():
    pass


@given(
    parsers.parse("an input molecule specified by '{input}'"),
    target_fixture="representations",
)
def representations(input):
    return [input]
