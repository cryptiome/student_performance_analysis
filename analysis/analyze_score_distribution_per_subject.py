# File: analysis/analyze_score_distribution_per_subject.py

from collections import defaultdict
from firebase.firebase_config import db

def analyze_score_distribution_per_subject(class_id: str):
    """
    Returns a dictionary showing how many students scored each score (0–10)
    for every subject in the specified class.
    """
    try:
        grades_ref = db.collection("grades").where("class_id", "==", class_id)
        grades_docs = grades_ref.stream()

        score_distribution = defaultdict(lambda: defaultdict(int))

        for doc in grades_docs:
            grade = doc.to_dict()
            subject_id = grade.get("subject_id")
            score = grade.get("score")

            if subject_id is not None and isinstance(score, (int, float)):
                rounded_score = round(score)
                score_distribution[subject_id][rounded_score] += 1

        # Convert nested defaultdicts to regular dicts for clean return
        return {subject_id: dict(score_map) for subject_id, score_map in score_distribution.items()}

    except Exception as e:
        print("حدث خطأ أثناء تحليل توزيع الدرجات:", str(e))
        return {}
