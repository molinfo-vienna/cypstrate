@cypstrate
Feature: Valid predictions

  Scenario Outline: Predictions are valid
    Given a random seed set to <seed>
    And a list of <num_molecules> random molecules, where <num_none> entries are None
    And the representations of the molecules in <input_type> format
    And the prediction mode is '<prediction_mode>'

    When the cypstrate model generates predictions for the molecule representations
    And the subset of the result where the preprocessed mol was not None is considered

    Then the result should contain the columns:
            prediction_1a2
            neighbor_1a2
            prediction_2a6
            neighbor_2a6
            prediction_2b6
            neighbor_2b6
            prediction_2c8
            neighbor_2c8
            prediction_2c9
            neighbor_2c9
            prediction_2c19
            neighbor_2c19
            prediction_2d6
            neighbor_2d6
            prediction_2e1
            neighbor_2e1
            prediction_3a4
            neighbor_3a4
    And the value in column 'prediction_1a2' should be one of ["Substrate", "Non-substrate", "No prediction"]
    And the value in column 'neighbor_1a2' should be between 0 and 1
    And the value in column 'prediction_2a6' should be one of ["Substrate", "Non-substrate", "No prediction"]
    And the value in column 'neighbor_2a6' should be between 0 and 1
    And the value in column 'prediction_2b6' should be one of ["Substrate", "Non-substrate", "No prediction"]
    And the value in column 'neighbor_2b6' should be between 0 and 1
    And the value in column 'prediction_2c8' should be one of ["Substrate", "Non-substrate", "No prediction"]
    And the value in column 'neighbor_2c8' should be between 0 and 1
    And the value in column 'prediction_2c9' should be one of ["Substrate", "Non-substrate", "No prediction"]
    And the value in column 'neighbor_2c9' should be between 0 and 1
    And the value in column 'prediction_2c19' should be one of ["Substrate", "Non-substrate", "No prediction"]
    And the value in column 'neighbor_2c19' should be between 0 and 1
    And the value in column 'prediction_2d6' should be one of ["Substrate", "Non-substrate", "No prediction"]
    And the value in column 'neighbor_2d6' should be between 0 and 1
    And the value in column 'prediction_2e1' should be one of ["Substrate", "Non-substrate", "No prediction"]
    And the value in column 'neighbor_2e1' should be between 0 and 1
    And the value in column 'prediction_3a4' should be one of ["Substrate", "Non-substrate", "No prediction"]
    And the value in column 'neighbor_3a4' should be between 0 and 1


  Examples:
  | seed | prediction_mode  | num_molecules | num_none | input_type |
  | 1    | best_performance | 10            | 0        | smiles     |
  | 2    | best_performance | 10            | 1        | smiles     |
  | 3    | best_performance | 10            | 2        | smiles     |
  | 4    | best_performance | 10            | 10       | smiles     |
  | 1    | full_coverage    | 10            | 0        | smiles     |
  | 2    | full_coverage    | 10            | 1        | smiles     |
  | 3    | full_coverage    | 10            | 2        | smiles     |
  | 4    | full_coverage    | 10            | 10       | smiles     |
