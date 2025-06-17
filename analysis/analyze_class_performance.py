import pandas as pd
from firebase.firebase_config import db

def analyze_class_performance(stage_id: str, class_id: str):
    # 1. Fetch students
    students_ref = db.collection("students").where("stage_id", "==", stage_id).where("class_id", "==", class_id)
    students = [doc.to_dict() for doc in students_ref.stream()]
    if not students:
        return {"status": "no_data", "message": "No students found for this class and stage."}

    students_df = pd.DataFrame(students)

    # 2. Fetch grades for those students
    grades_ref = db.collection("grades").where("class_id", "==", class_id)
    grades = [doc.to_dict() for doc in grades_ref.stream()]
    
    # Safety check: empty or missing student_id
    if not grades or not all("student_id" in g for g in grades):
        return {"status": "no_data", "message": "No valid grades found for this class."}
    
    grades_df = pd.DataFrame(grades)

    # Ensure 'student_id' exists in columns before filtering
    if "student_id" not in grades_df.columns:
        return {"status": "error", "message": "'student_id' field missing in grades data."}

    # 3. Filter only grades for valid students
    student_ids = students_df["student_id"].tolist()
    grades_df = grades_df[grades_df["student_id"].isin(student_ids)]
    if grades_df.empty:
        return {"status": "no_data", "message": "No grades found for matching students."}

    # 4. Fetch subjects
    subjects_ref = db.collection("subjects")
    subjects = {doc.id: doc.to_dict().get("name", "") for doc in subjects_ref.stream()}
    grades_df["subject_name"] = grades_df["subject_id"].map(subjects)

    # 5. Merge student names into grades
    merged = pd.merge(grades_df, students_df[["student_id", "name"]], on="student_id", how="left")

    # 6. Average score per student
    avg_scores = merged.groupby(["student_id", "name"])["score"].mean().reset_index()
    avg_scores.rename(columns={"score": "average_score"}, inplace=True)

    # 7. Category
    def classify(avg):
        if avg >= 8.5:
            return "ممتازة"
        elif avg >= 5:
            return "متوسطة"
        else:
            return "ضعيفة"
    avg_scores["category"] = avg_scores["average_score"].apply(classify)

    # 8. Weakest subject per student
    student_subject_avg = merged.groupby(["student_id", "subject_name"])["score"].mean().reset_index()
    weakest_subjects = student_subject_avg.sort_values(["student_id", "score"]).drop_duplicates("student_id", keep="first")
    weakest_subjects.rename(columns={"subject_name": "weakest_subject"}, inplace=True)

    # 9. Merge everything
    final = pd.merge(avg_scores, weakest_subjects[["student_id", "weakest_subject"]], on="student_id", how="left")

    return {
        "status": "success",
        "results": final.to_dict(orient="records")
    }
