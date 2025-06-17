import numpy as np
from sklearn.linear_model import LinearRegression
from firebase.firebase_config import db  

def predict_next_test_score(student_id: str, subject_id: str):
    """
    Train a Linear Regression model to predict the next score of a student
    based on their historical test scores in a specific subject.
    """
    try:
        # Step 1: Fetch test scores for student in a specific subject
        grades_ref = db.collection("grades")
        query = grades_ref.where("student_id", "==", student_id).where("subject_id", "==", subject_id)
        docs = query.stream()

        test_numbers = []
        scores = []

        for doc in docs:
            data = doc.to_dict()
            if "test_number" in data and "score" in data:
                test_numbers.append(data["test_number"])
                scores.append(data["score"])

        # Step 2: Validate sufficient data
        if len(test_numbers) < 2:
            return {
                "status": "error",
                "message": "Not enough data to train a regression model."
            }

        # Step 3: Train the regression model
        X = np.array(test_numbers).reshape(-1, 1)
        y = np.array(scores)
        model = LinearRegression()
        model.fit(X, y)

        # Step 4: Predict the next score
        next_test_number = max(test_numbers) + 1
        predicted_score = model.predict(np.array([[next_test_number]]))[0]

        return {
            "status": "success",
            "student_id": student_id,
            "subject_id": subject_id,
            "next_test_number": next_test_number,
            "predicted_score": round(predicted_score, 2)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
