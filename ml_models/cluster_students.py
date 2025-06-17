import pandas as pd
from sklearn.cluster import KMeans
from firebase.firebase_config import db
import numpy as np

def cluster_students_by_performance(class_id: str, n_clusters: int = 3):
    try:
        # Step 1: Fetch students and their scores
        students_ref = db.collection("students").where("class_id", "==", class_id)
        students = [doc.to_dict() | {"student_id": doc.id} for doc in students_ref.stream()]
        if not students:
            return {"status": "error", "message": "No students found."}
        student_map = {s["student_id"]: s["name"] for s in students}

        grades_ref = db.collection("grades").where("class_id", "==", class_id)
        grades = [doc.to_dict() for doc in grades_ref.stream()]
        if not grades:
            return {"status": "error", "message": "No grades found."}

        df = pd.DataFrame(grades)
        df["score"] = df["score"].astype(float)

        # Step 2: Group scores per student
        grouped = df.groupby("student_id")["score"].agg(["mean", "std", "count"])
        grouped.rename(columns={"mean": "average_score", "std": "score_std_dev"}, inplace=True)
        grouped.fillna(0, inplace=True)

        # Step 3: Add difficulty: subjects where score < 5
        difficulty = df[df["score"] < 5].groupby("student_id").size().rename("difficulty_subjects")
        grouped = grouped.join(difficulty, how="left").fillna(0)
        grouped["difficulty_subjects"] = grouped["difficulty_subjects"].astype(int)

        # Step 4: Clustering
        features = grouped[["average_score", "score_std_dev", "difficulty_subjects"]]
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        grouped["cluster"] = model.fit_predict(features)

        # Step 5: Assign real academic labels based on score
        centers = model.cluster_centers_
        sorted_indices = sorted(range(len(centers)), key=lambda i: centers[i][0], reverse=True)
        label_map = {}

        for i, idx in enumerate(sorted_indices):
            if i == 0:
                label_map[idx] = "Excellent"
            elif i == 1:
                label_map[idx] = "Average"
            else:
                label_map[idx] = "Weak"

        grouped["group"] = grouped["cluster"].map(label_map)

        # Step 6: Return results
        result = []
        for student_id, row in grouped.iterrows():
            result.append({
                "student_id": student_id,
                "name": student_map.get(student_id, "Unknown"),
                "average_score": round(row["average_score"], 2),
                "score_std_dev": round(row["score_std_dev"], 2),
                "difficulty_subjects": int(row["difficulty_subjects"]),
                "group": row["group"]
            })

        return {"status": "success", "clusters": result}

    except Exception as e:
        return {"status": "error", "message": str(e)}
