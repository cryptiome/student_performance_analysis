from firebase.firebase_config import db
import pandas as pd

def fetch_students():
    students_ref = db.collection("students").stream()
    return pd.DataFrame([doc.to_dict() for doc in students_ref])

def fetch_grades():
    grades_ref = db.collection("grades").stream()
    return pd.DataFrame([doc.to_dict() for doc in grades_ref])

def fetch_subjects():
    subjects_ref = db.collection("subjects").stream()
    return pd.DataFrame([doc.to_dict() for doc in subjects_ref])

def fetch_classes():
    classes_ref = db.collection("classes").stream()
    return pd.DataFrame([doc.to_dict() for doc in classes_ref])

def fetch_stages():
    stages_ref = db.collection("stages").stream()
    return pd.DataFrame([doc.to_dict() for doc in stages_ref])
