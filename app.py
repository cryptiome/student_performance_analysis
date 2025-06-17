from flask import Flask, jsonify, request
from flask_cors import CORS
from firebase.firebase_config import db

from analysis.analyze_class_performance import analyze_class_performance
from analysis.analyze_teacher_skill_influence import analyze_teacher_skill_influence
from analysis.analyze_correlation_between_subjects import analyze_correlation_between_subjects
from analysis.analyze_teacher_student_performance import analyze_teacher_student_performance
from analysis.analyze_score_distribution_per_subject import analyze_score_distribution_per_subject

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "API is working!"})

@app.route("/students")
def get_students():
    try:
        students = [doc.to_dict() for doc in db.collection("students").stream()]
        return jsonify({"status": "success", "data": students})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/analyze_class_performance")
def api_analyze_class_performance():
    stage_id = request.args.get("stage_id")
    class_id = request.args.get("class_id")
    if not stage_id or not class_id:
        return jsonify({"status": "error", "message": "Missing 'stage_id' or 'class_id' parameter."})
    result = analyze_class_performance(stage_id, class_id)
    return jsonify(result)

@app.route("/analyze_teacher_skill_influence")
def api_analyze_teacher_skill_influence():
    try:
        result = analyze_teacher_skill_influence()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/analyze_correlation_between_subjects', methods=['GET'])
def api_analyze_correlation_between_subjects():
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({"status": "error", "message": "Missing class_id parameter"}), 400
    try:
        result = analyze_correlation_between_subjects(class_id)
        if isinstance(result, dict) and "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 404
        return jsonify({"status": "success", "correlations": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/analyze_teacher_student_performance', methods=['GET'])
def api_analyze_teacher_student_performance():
    teacher_id = request.args.get('teacher_id')
    if not teacher_id:
        return jsonify({"status": "error", "message": "Missing 'teacher_id' parameter."}), 400
    try:
        result = analyze_teacher_student_performance(teacher_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/score-distribution", methods=["GET"])
def api_analyze_score_distribution_per_subject():
    class_id = request.args.get("class_id")
    if not class_id:
        return jsonify({"status": "error", "message": "Missing 'class_id' parameter."}), 400
    try:
        result = analyze_score_distribution_per_subject(class_id)
        return jsonify({"status": "success", "distribution": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/performance-trend", methods=["GET"])
def api_analyze_performance_trend_per_student():
    student_id = request.args.get("student_id")
    subject_id = request.args.get("subject_id")
    if not student_id or not subject_id:
        return jsonify({"status": "error", "message": "Missing 'student_id' or 'subject_id' parameter."}), 400
    from analysis.analyze_performance_trend_per_student import analyze_performance_trend_per_student
    result = analyze_performance_trend_per_student(student_id, subject_id)
    return jsonify(result)

@app.route("/api/skill-weakness", methods=["GET"])
def api_analyze_skill_weakness_per_student():
    class_id = request.args.get("class_id")
    if not class_id:
        return jsonify({"status": "error", "message": "Missing 'class_id' parameter."}), 400
    from analysis.analyze_skill_weakness_per_student import analyze_skill_weakness_per_student
    result = analyze_skill_weakness_per_student(class_id)
    return jsonify(result)

@app.route("/api/best-worst-subjects", methods=["GET"])
def api_analyze_best_worst_subjects_per_class():
    class_id = request.args.get("class_id")
    if not class_id:
        return jsonify({"status": "error", "message": "Missing 'class_id' parameter."}), 400
    from analysis.analyze_best_worst_subjects_per_class import analyze_best_worst_subjects_per_class
    result = analyze_best_worst_subjects_per_class(class_id)
    return jsonify(result)

@app.route('/api/student-scores-summary', methods=['GET'])
def api_student_scores_summary():
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({"status": "error", "message": "Missing 'class_id' parameter."}), 400
    from analysis.analyze_student_scores_summary import analyze_student_scores_summary
    result = analyze_student_scores_summary(class_id)
    return jsonify(result)

@app.route('/api/support-groups', methods=['GET'])
def api_generate_student_support_grouping():
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({"status": "error", "message": "Missing 'class_id' parameter."}), 400
    from analysis.generate_student_support_grouping import generate_student_support_grouping
    result = generate_student_support_grouping(class_id)
    return jsonify(result)

@app.route('/api/class-dashboard', methods=['GET'])
def api_generate_class_dashboard_report():
    class_id = request.args.get("class_id")
    if not class_id:
        return jsonify({"status": "error", "message": "Missing 'class_id' parameter."}), 400
    from analysis.generate_class_dashboard_report import generate_class_dashboard_report
    result = generate_class_dashboard_report(class_id)
    return jsonify(result)

@app.route("/api/predict-next-score", methods=["GET"])
def api_predict_next_test_score():
    student_id = request.args.get("student_id")
    subject_id = request.args.get("subject_id")
    if not student_id or not subject_id:
        return jsonify({"status": "error", "message": "Missing student_id or subject_id"}), 400
    from ml_models.linear_regression_predictor import predict_next_test_score
    result = predict_next_test_score(student_id, subject_id)
    return jsonify(result)

@app.route("/api/classify-performance", methods=["GET"])
def classify_performance():
    class_id = request.args.get("class_id")
    if not class_id:
        return jsonify({"status": "error", "message": "Missing class_id"}), 400
    from ml_models.classify_student_performance import classify_student_performance
    result = classify_student_performance(class_id)
    return jsonify(result)

@app.route("/api/cluster-student-performance", methods=["GET"])
def api_cluster_student_performance():
    class_id = request.args.get("class_id")
    if not class_id:
        return jsonify({"status": "error", "message": "Missing class_id parameter."})
    from ml_models.cluster_students import cluster_students_by_performance
    result = cluster_students_by_performance(class_id)
    return jsonify(result)

@app.route('/api/evaluate-models', methods=['GET'])
def evaluate_models():
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({"status": "error", "message": "Missing class_id"}), 400
    from ml_models.model_evaluation import evaluate_models_for_class
    result = evaluate_models_for_class(class_id)
    return jsonify(result)
