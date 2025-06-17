from firebase.firebase_config import db
import pandas as pd

def analyze_correlation_between_subjects(class_id):
    """
    Calculates Pearson correlation coefficients between all subjects
    based on students' scores in the specified class.

    Returns a list of subject pairs with their correlation coefficient.
    """
    # Fetch grades for the given class
    grades_ref = db.collection("grades")
    grades = grades_ref.where("class_id", "==", class_id).stream()
    grades_data = [doc.to_dict() for doc in grades]

    if not grades_data:
        return {"error": "No grades data found for this class."}

    grades_df = pd.DataFrame(grades_data)

    if "student_id" not in grades_df.columns or "subject_id" not in grades_df.columns or "score" not in grades_df.columns:
        return {"error": "Missing required fields in grades data."}

    # Pivot table: rows = student_id, columns = subject_id, values = score
    pivot_df = grades_df.pivot_table(
        index="student_id",
        columns="subject_id",
        values="score",
        aggfunc="mean"
    )

    pivot_df = pivot_df.dropna(axis=0, thresh=2)  # At least 2 subjects

    if pivot_df.empty:
        return {"error": "Not enough data to calculate correlations."}

    # Calculate Pearson correlation matrix
    correlation_matrix = pivot_df.corr(method="pearson")

    # Convert to list of dictionaries for JSON response
    correlation_list = []
    for col1 in correlation_matrix.columns:
        for col2 in correlation_matrix.columns:
            if col1 < col2:  # Avoid duplicates and self-correlation
                correlation_list.append({
                    "subject_1": col1,
                    "subject_2": col2,
                    "correlation": round(correlation_matrix.loc[col1, col2], 2)
                })

    return correlation_list
