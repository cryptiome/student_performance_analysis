from firebase.firebase_config import db

def analyze_skill_weakness_per_student(class_id):
    try:
        # Step 1: Fetch all students in the class
        students_ref = db.collection("students").where("class_id", "==", class_id)
        students_docs = students_ref.stream()
        students = {doc.id: doc.to_dict() for doc in students_docs}

        if not students:
            return {"status": "error", "message": "No students found in the class."}

        # Step 2: Fetch all subjects with skills
        subjects_ref = db.collection("subjects")
        subjects_docs = subjects_ref.stream()
        subjects = {doc.id: doc.to_dict() for doc in subjects_docs}

        if not subjects:
            return {"status": "error", "message": "No subjects found."}

        # Step 3: Fetch grades for these students
        grades_ref = db.collection("grades").where("class_id", "==", class_id)
        grades_docs = grades_ref.stream()

        student_subject_scores = {}
        for grade in grades_docs:
            data = grade.to_dict()
            sid = data.get("student_id")
            subject_id = data.get("subject_id")
            score = data.get("score")

            if sid not in student_subject_scores:
                student_subject_scores[sid] = {}

            if subject_id not in student_subject_scores[sid]:
                student_subject_scores[sid][subject_id] = []

            student_subject_scores[sid][subject_id].append(score)

        # Step 4: Analyze weakest subject and its skills per student
        result = []
        for sid, subject_scores in student_subject_scores.items():
            avg_scores = {
                subj_id: sum(scores) / len(scores)
                for subj_id, scores in subject_scores.items()
            }
            if not avg_scores:
                continue

            weakest_subject_id = min(avg_scores, key=avg_scores.get)
            weakest_subject = subjects.get(weakest_subject_id, {})
            student_name = students[sid]["name"] if sid in students else "Unknown"

            result.append({
                "student_id": sid,
                "name": student_name,
                "weakest_subject": weakest_subject.get("name", "Unknown"),
                "skills": weakest_subject.get("skills", [])
            })

        return {"status": "success", "results": result}

    except Exception as e:
        return {"status": "error", "message": str(e)}
