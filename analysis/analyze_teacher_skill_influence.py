from firebase.firebase_config import db
import pandas as pd

def analyze_teacher_skill_influence():
    # Step 1: Fetch all relevant collections
    students = [doc.to_dict() for doc in db.collection("students").stream()]
    grades = [doc.to_dict() for doc in db.collection("grades").stream()]
    subjects = [doc.to_dict() for doc in db.collection("subjects").stream()]
    teachers = [doc.to_dict() for doc in db.collection("teachers").stream()]

    if not students or not grades or not subjects or not teachers:
        return {"status": "no_data", "message": "Missing data in one or more collections."}

    students_df = pd.DataFrame(students)
    grades_df = pd.DataFrame(grades)
    subjects_df = pd.DataFrame(subjects)
    teachers_df = pd.DataFrame(teachers)

    # Step 2: Ensure teacher_id is present
    if "subject_id" not in teachers_df.columns or "teacher_id" not in teachers_df.columns:
        return {"status": "error", "message": "Missing teacher_id or subject_id in teachers data."}

    # Step 3: Merge grades with students
    merged_df = pd.merge(grades_df, students_df[["student_id", "name"]], on="student_id", how="left")

    # Step 4: Merge with subjects to get subject name and skills
    subjects_df = subjects_df.rename(columns={"subject_id": "subject_id", "name": "subject_name"})
    merged_df = pd.merge(merged_df, subjects_df[["subject_id", "subject_name", "skills"]], on="subject_id", how="left")

    # Step 5: Merge with teachers using subject_id to get teacher info
    merged_df = pd.merge(merged_df, teachers_df[["subject_id", "teacher_id", "name"]].rename(columns={"name": "teacher_name"}), on="subject_id", how="left")

    # Step 6: Group and summarize
    grouped = merged_df.groupby(["teacher_id", "teacher_name", "subject_name"]).agg({
        "score": "mean"
    }).reset_index()

    grouped.rename(columns={"score": "average_score"}, inplace=True)

    return {
        "status": "success",
        "results": grouped.to_dict(orient="records")
    }
