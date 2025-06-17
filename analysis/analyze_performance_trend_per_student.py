from firebase.firebase_config import db

def analyze_performance_trend_per_student(student_id: str, subject_id: str):
    try:
        # Query all grades for this student in this subject
        grades_ref = db.collection("grades")
        query = grades_ref.where("student_id", "==", student_id).where("subject_id", "==", subject_id)
        docs = query.stream()

        # Collect scores with their test number
        scores = []
        for doc in docs:
            data = doc.to_dict()
            scores.append((data["test_number"], data["score"]))

        # Sort by test_number ascending
        scores.sort(key=lambda x: x[0])

        trend = [{"test_number": test, "score": score} for test, score in scores]

        return {
            "status": "success",
            "student_id": student_id,
            "subject_id": subject_id,
            "trend": trend
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
