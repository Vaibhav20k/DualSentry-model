import joblib
from pathlib import Path

from sklearn.ensemble import IsolationForest

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

MODEL_DIR = BASE_DIR / "models" / "saved_models"

RANDOM_STATE = 42


def load_training_data():

    print("=" * 60)
    print("Loading Training Data...")
    print("=" * 60)

    X_train = joblib.load(
        PROCESSED_DIR / "X_train.pkl"
    )

    y_train = joblib.load(
        PROCESSED_DIR / "y_train.pkl"
    )

    print(f"X_train Shape : {X_train.shape}")
    print(f"y_train Shape : {y_train.shape}")

    return X_train, y_train


def build_model():

    print("\nCreating Isolation Forest...")

    model = IsolationForest(

        n_estimators=200,

        contamination=0.036,

        random_state=RANDOM_STATE,

        n_jobs=-1,

        verbose=1,

    )

    return model

#TRAIN MODEL

def train_model(
    model,
    X_train,
):

    print("\nTraining Isolation Forest...")

    model.fit(X_train)

    print("Training Complete.")

    return model

#SAVE IT

def save_model(model):

    joblib.dump(

        model,

        MODEL_DIR / "isolation_forest.pkl",

    )

    print("\nModel Saved Successfully.")

#MAIN 

def main():

    X_train, y_train = load_training_data()

    model = build_model()

    model = train_model(

        model,

        X_train,

    )

    save_model(model)


if __name__ == "__main__":

    main()