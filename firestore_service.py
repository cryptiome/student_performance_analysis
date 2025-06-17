from firebase.firebase_config import connect_to_firebase

db = connect_to_firebase()

def get_students_data(stage_id=None, class_id=None):
    ref = db.collection("students")
    if stage_id and class_id:
        query = ref.where("stage_id", "==", stage_id).where("class_id", "==", class_id)
    elif stage_id:
        query = ref.where("stage_id", "==", stage_id)
    elif class_id:
        query = ref.where("class_id", "==", class_id)
    else:
        query = ref
    return [dict(doc.to_dict(), student_id=doc.id) for doc in query.stream()]

def get_grades_data(class_id=None):
    ref = db.collection("grades")
    if class_id:
        query = ref.where("class_id", "==", class_id)
    else:
        query = ref
    return [dict(doc.to_dict(), grade_id=doc.id) for doc in query.stream()]

def get_subjects_data():
    ref = db.collection("subjects").stream()
    return [dict(doc.to_dict(), subject_id=doc.id) for doc in ref]

def get_classes_data(stage_id=None):
    ref = db.collection("classes")
    if stage_id:
        query = ref.where("stage_id", "==", stage_id)
    else:
        query = ref
    return [dict(doc.to_dict(), class_id=doc.id) for doc in query.stream()]

def get_teachers_data(stage_id=None, subject_id=None):
    ref = db.collection("teachers")
    if stage_id and subject_id:
        query = ref.where("stage_id", "==", stage_id).where("subject_id", "==", subject_id)
    elif stage_id:
        query = ref.where("stage_id", "==", stage_id)
    elif subject_id:
        query = ref.where("subject_id", "==", subject_id)
    else:
        query = ref
    return [dict(doc.to_dict(), teacher_id=doc.id) for doc in query.stream()]

def get_stages_data():
    ref = db.collection("stages").stream()
    return [dict(doc.to_dict(), stage_id=doc.id) for doc in ref]
