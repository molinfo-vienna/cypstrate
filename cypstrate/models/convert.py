import joblib
import glob
from cypstrate.models import ConsensusClassifier, NonBinaryScaler
from sklearn.pipeline import Pipeline


def patch(clf, level=0):
    clf_type = type(clf).__name__

    if clf_type == "ConsensusClassifier":
        print("  " * level + "Patch ConsensusClassifier")

        # collect all properties to copy
        properties_to_copy = [
            "estimators",
            "input_sizes",
            "voting",
            "prob_threshold",
            "min_consensus",
        ]
        properties = {p: getattr(clf, p) for p in properties_to_copy}

        # estimators have to be patched, too
        properties["estimators"] = [
            patch(estimator, level + 1) for estimator in properties["estimators"]
        ]

        # convert ConsensusClassifier to cypstrate.ConsensusClassifier
        clf_patch = ConsensusClassifier(**properties)

        # copy additional properties (not necessary for constructor)
        additional_properties = ["classes_", "n_features_"]
        for p in additional_properties:
            setattr(clf_patch, p, getattr(clf, p))
        setattr(clf_patch, "estimators_", clf_patch.estimators)
    elif clf_type == "Pipeline":
        print("  " * level + "Patch Pipeline")

        # patch all pipeline steps
        steps = [(label, patch(estimator, level + 1)) for label, estimator in clf.steps]
        clf_patch = Pipeline(steps)
    elif clf_type == "NonBinaryScaler":
        print("  " * level + "Patch NonBinaryScaler")

        # collect all properties to copy
        properties_to_copy = ["with_mean", "with_std"]
        properties = {p: getattr(clf, p) for p in properties_to_copy}

        # convert NonBinaryScaler to cypstrate.NonBinaryScaler
        clf_patch = NonBinaryScaler(**properties)

        # copy additional properties (not necessary for constructor)
        additional_properties = ["nonbinary_mask", "scaler"]
        for p in additional_properties:
            setattr(clf_patch, p, getattr(clf, p))
    else:
        print("  " * level + "Patch", clf_type)
        clf_patch = clf

    return clf_patch


# iterate through all joblib files in all subdirectories
for filename in glob.glob("./**/*.joblib"):
    print(filename)

    # load joblib file
    with open(filename, "rb") as f:
        clf = joblib.load(f)

    # patch old classes with new classes
    clf_patch = patch(clf)

    print(set(dir(clf)) - set(dir(clf_patch)))

    filename_patch = filename
    with open(filename_patch, "wb") as f:
        joblib.dump(clf_patch, f)
