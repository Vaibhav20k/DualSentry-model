import joblib
from pathlib import Path

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
)

#PATH

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

MODEL_DIR = BASE_DIR / "models" / "saved_models"

#LOADING TEST DATA 
def load_data():

    print("=" * 60)
    print("Loading Test Dataset...")
    print("=" * 60)

    X_test = joblib.load(
        PROCESSED_DIR / "X_test.pkl"
    )

    y_test = joblib.load(
        PROCESSED_DIR / "y_test.pkl"
    )

    model = joblib.load(
        MODEL_DIR / "isolation_forest.pkl"
    )

    return X_test, y_test, model

#PREDICTION 
def predict(
    model,
    X_test,
):

    print("\nRunning predictions...")

    predictions = model.predict(X_test)

    return predictions

#PREDICTION CONVERTER

def convert_predictions(predictions):

    predictions = [
        1 if p == -1 else 0
        for p in predictions
    ]

    return predictions

#EVALUATION 
def evaluate(
    y_true,
    y_pred,
):

    print("\n")
    print("=" * 60)
    print("Evaluation")
    print("=" * 60)

    print(
        "\nAccuracy :",
        accuracy_score(
            y_true,
            y_pred,
        ),
    )

    print(
        "Precision:",
        precision_score(
            y_true,
            y_pred,
            zero_division=0,
        ),
    )

    print(
        "Recall   :",
        recall_score(
            y_true,
            y_pred,
            zero_division=0,
        ),
    )

    print(
        "F1 Score :",
        f1_score(
            y_true,
            y_pred,
            zero_division=0,
        ),
    )

    print("\nConfusion Matrix")

    print(
        confusion_matrix(
            y_true,
            y_pred,
        )
    )

    print("\nClassification Report")

    print(
        classification_report(
            y_true,
            y_pred,
            zero_division=0,
        )
    )

#MAIN
def main():

    X_test, y_test, model = load_data()

    predictions = predict(
        model,
        X_test,
    )

    predictions = convert_predictions(
        predictions,
    )

    evaluate(
        y_test,
        predictions,
    )


if __name__ == "__main__":

    main()    