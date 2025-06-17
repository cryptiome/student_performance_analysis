from firebase.firebase_config import db

def analyze_best_worst_subjects_per_class(class_id):
    try:
        grades_ref = db.collection("grades").where("class_id", "==", class_id)
        grades_docs = grades_ref.stream()

        subject_scores = {}
        subject_counts = {}

        for doc in grades_docs:
            data = doc.to_dict()
            subject_id = data.get("subject_id")
            score = data.get("score")

            if subject_id is not None and isinstance(score, (int, float)):
                subject_scores[subject_id] = subject_scores.get(subject_id, 0) + score
                subject_counts[subject_id] = subject_counts.get(subject_id, 0) + 1

        if not subject_scores:
            return {"status": "info", "message": "No scores found for this class."}

        average_scores = {
            sid: subject_scores[sid] / subject_counts[sid]
            for sid in subject_scores
        }

        best_subject_id = max(average_scores, key=average_scores.get)
        worst_subject_id = min(average_scores, key=average_scores.get)

        def get_subject_name(subject_id):
            doc = db.collection("subjects").document(subject_id).get()
            return doc.to_dict().get("name", "Unknown") if doc.exists else "Unknown"

        return {
            "status": "success",
            "best_subject": {
                "id": best_subject_id,
                "name": get_subject_name(best_subject_id),
                "average_score": round(average_scores[best_subject_id], 2)
            },
            "worst_subject": {
                "id": worst_subject_id,
                "name": get_subject_name(worst_subject_id),
                "average_score": round(average_scores[worst_subject_id], 2)
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
