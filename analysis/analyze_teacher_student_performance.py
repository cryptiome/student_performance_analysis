import pandas as pd
from firebase.firebase_config import db

def analyze_teacher_student_performance(teacher_id: str):
    # 1. Fetch teacher info (to get subject_id and stage_id)
    teacher_ref = db.collection("teachers").document(teacher_id).get()
    if not teacher_ref.exists:
        return {"status": "error", "message": "Teacher not found."}

    teacher_data = teacher_ref.to_dict()
    subject_id = teacher_data.get("subject_id")
    stage_id = teacher_data.get("stage_id")
    teacher_name = teacher_data.get("name", "")

    if not subject_id or not stage_id:
        return {"status": "error", "message": "Teacher data is incomplete."}

    # 2. Fetch students in the teacher's stage
    students_ref = db.collection("students").where("stage_id", "==", stage_id)
    students = [doc.to_dict() for doc in students_ref.stream()]
    if not students:
        return {"status": "no_data", "message": "No students found for this stage."}
    students_df = pd.DataFrame(students)

    # 3. Fetch grades for those students in the teacher's subject
    student_ids = students_df["student_id"].tolist()
    grades_ref = db.collection("grades")
    grades = [doc.to_dict() for doc in grades_ref.stream()]
    grades_df = pd.DataFrame(grades)
    grades_df = grades_df[grades_df["student_id"].isin(student_ids)]
    grades_df = grades_df[grades_df["subject_id"] == subject_id]

    if grades_df.empty:
        return {"status": "no_data", "message": "No grades found for these students in this subject."}

    # 4. Fetch subject name
    subject_doc = db.collection("subjects").document(subject_id).get()
    subject_name = subject_doc.to_dict().get("name", "") if subject_doc.exists else "Unknown"

    # 5. Merge student names
    merged = pd.merge(grades_df, students_df[["student_id", "name"]], on="student_id", how="left")

    # 6. Group and format output
    grouped = merged.groupby(["student_id", "name"])["score"].mean().reset_index()
    grouped.rename(columns={
        "name": "student_name",
        "score": "average_score"
    }, inplace=True)
    grouped["teacher_name"] = teacher_name
    grouped["subject_id"] = subject_id
    grouped["subject_name"] = subject_name

    return {
        "status": "success",
        "results": grouped.to_dict(orient="records")
    }
