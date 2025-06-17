from firebase.firebase_config import db
from statistics import mean
from collections import defaultdict

def generate_class_dashboard_report(class_id: str):
    try:
        # Fetch students
        students_ref = db.collection("students").where("class_id", "==", class_id)
        students = [doc.to_dict() for doc in students_ref.stream()]
        student_count = len(students)

        # Fetch grades
        grades_ref = db.collection("grades").where("class_id", "==", class_id)
        grades = [doc.to_dict() for doc in grades_ref.stream()]
        if not grades:
            return {"status": "no_data", "message": "No grades found."}

        # Compute average class score
        all_scores = [g["score"] for g in grades if isinstance(g.get("score"), (int, float))]
        class_average = round(mean(all_scores), 2) if all_scores else 0

        # Group scores by subject
        subject_scores = defaultdict(list)
        for g in grades:
            subject_scores[g["subject_id"]].append(g["score"])

        # Get subject names
        subjects_ref = db.collection("subjects")
        subjects = {doc.id: doc.to_dict().get("name", "Unknown") for doc in subjects_ref.stream()}
        subject_count = len(subjects)

        # Calculate average per subject
        subject_averages = {
            sid: round(mean(scores), 2)
            for sid, scores in subject_scores.items()
            if scores
        }

        best_subject_id = max(subject_averages, key=subject_averages.get)
        worst_subject_id = min(subject_averages, key=subject_averages.get)

        # Grouping counts
        group_counts = {"Excellent": 0, "Average": 0, "Weak": 0}
        for s_id in set([g["student_id"] for g in grades]):
            scores = [g["score"] for g in grades if g["student_id"] == s_id]
            if not scores:
                continue
            avg = mean(scores)
            if avg < 6.0:
                group_counts["Weak"] += 1
            elif avg < 8.0:
                group_counts["Average"] += 1
            else:
                group_counts["Excellent"] += 1

        return {
            "status": "success",
            "dashboard": {
                "student_count": student_count,
                "subject_count": subject_count,
                "class_average_score": class_average,
                "best_subject": {
                    "id": best_subject_id,
                    "name": subjects.get(best_subject_id, "Unknown"),
                    "average_score": subject_averages[best_subject_id]
                },
                "worst_subject": {
                    "id": worst_subject_id,
                    "name": subjects.get(worst_subject_id, "Unknown"),
                    "average_score": subject_averages[worst_subject_id]
                },
                "group_counts": group_counts
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
