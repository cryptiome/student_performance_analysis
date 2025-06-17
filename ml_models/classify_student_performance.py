from sklearn.tree import DecisionTreeClassifier
import numpy as np
from firebase.firebase_config import db

def classify_student_performance(class_id: str):
    try:
        # Step 1: Fetch all students in the class
        students_ref = db.collection("students").where("class_id", "==", class_id)
        students = [doc.to_dict() | {"student_id": doc.id} for doc in students_ref.stream()]
        if not students:
            return {"status": "error", "message": "No students found in class."}

        # Step 2: Fetch grades
        grades_ref = db.collection("grades").where("class_id", "==", class_id)
        grades = [doc.to_dict() for doc in grades_ref.stream()]
        if not grades:
            return {"status": "error", "message": "No grades found in class."}

        # Step 3: Preprocess – build student average and std deviation (variance)
        student_scores = {}
        for grade in grades:
            sid = grade.get("student_id")
            score = grade.get("score")

            if sid not in student_scores:
                student_scores[sid] = []
            student_scores[sid].append(score)

        features = []
        labels = []
        student_ids = []

        for student in students:
            sid = student["student_id"]
            scores = student_scores.get(sid, [])
            if len(scores) < 2:
                continue  # skip student with not enough data

            avg = np.mean(scores)
            std = np.std(scores)

            # Assign label manually based on average (used for training)
            if avg >= 8:
                label = "Excellent"
            elif avg >= 6:
                label = "Average"
            else:
                label = "Weak"

            features.append([avg, std])
            labels.append(label)
            student_ids.append(sid)

        if not features:
            return {"status": "error", "message": "Not enough data to train classifier."}

        # Step 4: Train the Decision Tree
        clf = DecisionTreeClassifier(max_depth=3)
        clf.fit(features, labels)

        # Step 5: Predict for each student
        results = []
        for i, sid in enumerate(student_ids):
            pred = clf.predict([features[i]])[0]
            results.append({
                "student_id": sid,
                "name": next((s["name"] for s in students if s["student_id"] == sid), "Unknown"),
                "category": pred,
                "average_score": round(features[i][0], 2),
                "score_std_dev": round(features[i][1], 2)
            })

        return {"status": "success", "results": results}

    except Exception as e:
        return {"status": "error", "message": str(e)}
