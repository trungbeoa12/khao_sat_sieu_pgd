from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.models import Base, SurveyResponse, User
import os
import pandas as pd
import numpy as np
import io
import csv

app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend")
CORS(app)

# Khởi tạo database
DATABASE_URL = "sqlite:///backend/survey.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    db = SessionLocal()
    user = db.query(User).filter(User.username == data["username"], User.password == data["password"]).first()
    db.close()
    if user:
        return jsonify({"message": "Đăng nhập thành công", "role": user.role, "username": user.username, "branch_id": user.branch_id})
    return jsonify({"error": "Sai tên đăng nhập hoặc mật khẩu"}), 401

@app.route("/submit_survey", methods=["POST"])
def submit_survey():
    data = request.json
    db = SessionLocal()
    survey = SurveyResponse(**data)
    db.add(survey)
    db.commit()
    db.refresh(survey)
    db.close()
    return jsonify({"message": "Khảo sát đã được gửi thành công!"})

@app.route("/export_survey_csv", methods=["GET"])
def export_survey_csv():
    db = SessionLocal()
    surveys = db.query(SurveyResponse).all()
    db.close()
    
    headers = ["id", "branch_id", "csvc", "csqd", "hotro", "proposal", "pgd_info", "other_pgd", "additional_comments"]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for s in surveys:
        writer.writerow([s.id, s.branch_id, s.csvc, s.csqd, s.hotro, s.proposal, s.pgd_info, s.other_pgd, s.additional_comments])
    output.seek(0)
    return send_from_directory(directory="backend", filename="survey.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

