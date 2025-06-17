# ml_models/model_evaluation.py

from firebase.firebase_config import db
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from sklearn.model_selection import train_test_split

def evaluate_models_for_class(class_id: str):
    try:
        # Step 1: Load grades data
        grades_ref = db.collection("grades").where("class_id", "==", class_id)
        grades_docs = [doc.to_dict() for doc in grades_ref.stream()]
        if not grades_docs:
            return {"status": "error", "message": "No grades found."}

        # Prepare regression data: predict next score from previous ones
        regression_data = {}
        for g in grades_docs:
            sid = g["student_id"]
            regression_data.setdefault((sid, g["subject_id"]), []).append(g["score"])

        X_reg, y_reg = [], []
        for (sid, sub), scores in regression_data.items():
            if len(scores) >= 2:
                for i in range(len(scores) - 1):
                    X_reg.append([scores[i]])
                    y_reg.append(scores[i + 1])

        if len(X_reg) < 10:
            return {"status": "error", "message": "Not enough regression samples"}

        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
        reg_model = LinearRegression().fit(X_train_r, y_train_r)
        y_pred_r = reg_model.predict(X_test_r)

        regression_metrics = {
            "MSE": round(mean_squared_error(y_test_r, y_pred_r), 3),
            "R2": round(r2_score(y_test_r, y_pred_r), 3)
        }

        # Prepare classification data
        student_scores = {}
        for g in grades_docs:
            sid = g["student_id"]
            student_scores.setdefault(sid, []).append(g["score"])

        X_clf, y_clf = [], []
        for sid, scores in student_scores.items():
            avg = sum(scores) / len(scores)
            stddev = np.std(scores)
            if avg >= 8:
                label = "Excellent"
            elif avg >= 6:
                label = "Average"
            else:
                label = "Weak"
            X_clf.append([avg, stddev])
            y_clf.append(label)

        if len(X_clf) < 10:
            return {"status": "error", "message": "Not enough classification samples"}

        X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_clf, y_clf, test_size=0.2, random_state=42)
        clf_model = DecisionTreeClassifier().fit(X_train_c, y_train_c)
        y_pred_c = clf_model.predict(X_test_c)

        classification_metrics = {
            "Accuracy": round(accuracy_score(y_test_c, y_pred_c), 3)
        }

        return {
            "status": "success",
            "regression_metrics": regression_metrics,
            "classification_metrics": classification_metrics
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
