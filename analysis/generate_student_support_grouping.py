import pandas as pd
from firebase.firebase_config import db

def generate_student_support_grouping(class_id: str):
    # 1. Fetch students in the class
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

    # 5. Categorize students
    def group_category(score):
        if score < 6.0:
            return "Weak"
        elif score < 8.0:
            return "Average"
        else:
            return "Excellent"

    grouped["group"] = grouped["average_score"].apply(group_category)

    # 6. Organize results by group
    support_groups = {
        "Excellent": [],
        "Average": [],
        "Weak": []
    }

    for _, row in grouped.iterrows():
        student_data = {
            "student_id": row["student_id"],
            "name": row["name"],
            "average_score": round(row["average_score"], 2)
        }
        support_groups[row["group"]].append(student_data)

    return {
        "status": "success",
        "support_groups": support_groups
    }
