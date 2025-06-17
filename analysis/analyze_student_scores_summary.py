import pandas as pd
from firebase.firebase_config import db

def analyze_student_scores_summary(class_id: str):
    # 1. Fetch students in this class
    students_ref = db.collection("students").where("class_id", "==", class_id)
    students = [doc.to_dict() for doc in students_ref.stream()]
    if not students:
        return {"status": "no_data", "message": "No students found for this class."}
    students_df = pd.DataFrame(students)

    # 2. Fetch grades for those students
    grades_ref = db.collection("grades").where("class_id", "==", class_id)
    grades = [doc.to_dict() for doc in grades_ref.stream()]
    if not grades:
        return {"status": "no_data", "message": "No grades found for this class."}
    grades_df = pd.DataFrame(grades)

    # 3. Merge grades with student names
    merged_df = pd.merge(grades_df, students_df[["student_id", "name"]], on="student_id", how="left")

    # 4. Group by student and calculate average score
    grouped = merged_df.groupby(["student_id", "name"])["score"].mean().reset_index()
    grouped.rename(columns={"score": "average_score"}, inplace=True)

    # 5. Add status based on threshold (e.g., 6.0)
    grouped["status"] = grouped["average_score"].apply(lambda x: "At Risk" if x < 6.0 else "Normal")

    return {
        "status": "success",
        "results": grouped.to_dict(orient="records")
    }
