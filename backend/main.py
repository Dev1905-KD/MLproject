import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

import io
import pandas as pd
import numpy as np
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.pipeline.predict_pipeline import PredictPipeline, CustomData
from src.pipeline.train_pipeline import TrainPipeline
from src.utils import load_object
from src.logger import logger

app = FastAPI(
    title="Student Performance Indicator API",
    description="ML backend service predicting student math performance based on demographic & score features",
    version="1.0.0",
)

# Enable CORS for local dev and web application integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StudentInputSchema(BaseModel):
    gender: str = Field(..., example="female", description="Gender of student ('female', 'male')")
    race_ethnicity: str = Field(..., example="group B", description="Ethnicity group ('group A', 'group B', 'group C', 'group D', 'group E')")
    parental_level_of_education: str = Field(
        ..., example="bachelor's degree", description="Parental education level"
    )
    lunch: str = Field(..., example="standard", description="Lunch type ('standard', 'free/reduced')")
    test_preparation_course: str = Field(
        ..., example="none", description="Test preparation course ('none', 'completed')"
    )
    reading_score: float = Field(..., ge=0, le=100, example=72.0, description="Reading score (0-100)")
    writing_score: float = Field(..., ge=0, le=100, example=74.0, description="Writing score (0-100)")


class PredictionResult(BaseModel):
    predicted_math_score: float
    grade: str
    performance_level: str
    percentile_estimate: float
    reading_score: float
    writing_score: float
    recommendations: List[str]
    input_summary: dict


def calculate_grade_and_level(score: float):
    if score >= 90:
        return "A+", "Exceptional Mastery", 95.0
    elif score >= 80:
        return "A", "High Achievement", 85.0
    elif score >= 70:
        return "B", "Solid Performance", 68.0
    elif score >= 60:
        return "C", "Moderate Proficiency", 48.0
    elif score >= 50:
        return "D", "Basic Passing", 28.0
    else:
        return "F", "Needs Significant Support", 10.0


def generate_recommendations(math_score: float, reading: float, writing: float, test_prep: str):
    recommendations = []
    if math_score < 60:
        recommendations.append("Focus on foundational math topics (algebra & arithmetic problem-solving).")
    if reading > math_score + 15:
        recommendations.append("Strong reading comprehension detected — try word-problem translation exercises to boost math scores.")
    if writing > math_score + 15:
        recommendations.append("Good structured writing skills — practice step-by-step mathematical proofs and problem explanations.")
    if test_prep.lower() == "none":
        recommendations.append("Enrolling in a structured Test Preparation Course is highly recommended.")
    if math_score >= 85:
        recommendations.append("Excellent quantitative aptitude — consider advanced STEM / calculus enrichment courses.")
    if not recommendations:
        recommendations.append("Maintain consistent practice with weekly review quizzes and target problem areas.")
    return recommendations


@app.get("/api/health")
def health_check():
    model_exists = os.path.exists(os.path.join(root_dir, "artifacts", "model.pkl"))
    preprocessor_exists = os.path.exists(os.path.join(root_dir, "artifacts", "preprocessor.pkl"))
    return {
        "status": "healthy",
        "artifacts": {
            "model": model_exists,
            "preprocessor": preprocessor_exists,
        },
        "model_loaded": model_exists and preprocessor_exists,
    }


@app.post("/api/predict", response_model=PredictionResult)
def predict_score(input_data: StudentInputSchema):
    try:
        custom_data = CustomData(
            gender=input_data.gender,
            race_ethnicity=input_data.race_ethnicity,
            parental_level_of_education=input_data.parental_level_of_education,
            lunch=input_data.lunch,
            test_preparation_course=input_data.test_preparation_course,
            reading_score=int(input_data.reading_score),
            writing_score=int(input_data.writing_score),
        )
        df_input = custom_data.get_data_as_data_frame()

        pipeline = PredictPipeline()
        predictions = pipeline.predict(df_input)
        raw_pred = float(predictions[0])
        pred_math = round(max(0.0, min(100.0, raw_pred)), 2)

        grade, level, percentile = calculate_grade_and_level(pred_math)
        recs = generate_recommendations(
            pred_math, input_data.reading_score, input_data.writing_score, input_data.test_preparation_course
        )

        return PredictionResult(
            predicted_math_score=pred_math,
            grade=grade,
            performance_level=level,
            percentile_estimate=percentile,
            reading_score=input_data.reading_score,
            writing_score=input_data.writing_score,
            recommendations=recs,
            input_summary=input_data.dict(),
        )

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predict-batch")
async def predict_batch(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Uploaded file must be a CSV file.")
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        required_cols = [
            "gender",
            "race_ethnicity",
            "parental_level_of_education",
            "lunch",
            "test_preparation_course",
            "reading_score",
            "writing_score",
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns in CSV: {', '.join(missing_cols)}",
            )

        pipeline = PredictPipeline()
        input_features = df[required_cols]
        raw_preds = pipeline.predict(input_features)

        df["predicted_math_score"] = [round(max(0.0, min(100.0, float(p))), 2) for p in raw_preds]
        df["grade"] = df["predicted_math_score"].apply(lambda s: calculate_grade_and_level(s)[0])
        df["performance_level"] = df["predicted_math_score"].apply(lambda s: calculate_grade_and_level(s)[1])

        records = df.to_dict(orient="records")

        summary = {
            "total_records": len(df),
            "avg_predicted_math": round(float(df["predicted_math_score"].mean()), 2),
            "max_predicted_math": round(float(df["predicted_math_score"].max()), 2),
            "min_predicted_math": round(float(df["predicted_math_score"].min()), 2),
            "grade_distribution": df["grade"].value_counts().to_dict(),
        }

        return {"summary": summary, "results": records}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch error: {str(e)}")


@app.get("/api/stats")
def get_dataset_stats():
    try:
        paths = [
            os.path.join(root_dir, "stud.csv"),
            os.path.join(root_dir, "notebook", "data", "stud.csv"),
            os.path.join(root_dir, "artifacts", "data.csv"),
        ]
        df = None
        for p in paths:
            if os.path.exists(p):
                df = pd.read_csv(p)
                break
        
        if df is None:
            raise HTTPException(status_code=444, detail="Dataset stud.csv not found")

        total_count = len(df)
        averages = {
            "math": round(float(df["math_score"].mean()), 2),
            "reading": round(float(df["reading_score"].mean()), 2),
            "writing": round(float(df["writing_score"].mean()), 2),
        }
        
        gender_stats = (
            df.groupby("gender")[["math_score", "reading_score", "writing_score"]]
            .mean()
            .round(2)
            .to_dict(orient="index")
        )
        
        test_prep_stats = (
            df.groupby("test_preparation_course")[["math_score", "reading_score", "writing_score"]]
            .mean()
            .round(2)
            .to_dict(orient="index")
        )

        parental_edu_stats = (
            df.groupby("parental_level_of_education")["math_score"]
            .mean()
            .round(2)
            .to_dict()
        )

        ethnicity_stats = (
            df.groupby("race_ethnicity")["math_score"]
            .mean()
            .round(2)
            .to_dict()
        )

        correlations = {
            "math_reading": round(float(df["math_score"].corr(df["reading_score"])), 3),
            "math_writing": round(float(df["math_score"].corr(df["writing_score"])), 3),
            "reading_writing": round(float(df["reading_score"].corr(df["writing_score"])), 3),
        }

        return {
            "total_students": total_count,
            "overall_averages": averages,
            "gender_breakdown": gender_stats,
            "test_prep_breakdown": test_prep_stats,
            "parental_edu_breakdown": parental_edu_stats,
            "ethnicity_breakdown": ethnicity_stats,
            "correlations": correlations,
        }

    except Exception as e:
        logger.error(f"Dataset stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/model-info")
def get_model_info():
    try:
        model_path = os.path.join(root_dir, "artifacts", "model.pkl")
        preprocessor_path = os.path.join(root_dir, "artifacts", "preprocessor.pkl")
        
        model_name = "Unknown"
        if os.path.exists(model_path):
            try:
                model = load_object(model_path)
                model_name = model.__class__.__name__
            except Exception:
                model_name = "Scikit-Learn Model"

        categorical_options = {
            "gender": ["female", "male"],
            "race_ethnicity": ["group A", "group B", "group C", "group D", "group E"],
            "parental_level_of_education": [
                "some high school",
                "high school",
                "some college",
                "associate's degree",
                "bachelor's degree",
                "master's degree",
            ],
            "lunch": ["standard", "free/reduced"],
            "test_preparation_course": ["none", "completed"],
        }

        features_numerical = ["reading_score", "writing_score"]
        target = "math_score"

        return {
            "model_name": model_name,
            "model_type": "Regression Pipeline (Preprocessing + Estimator)",
            "target_variable": target,
            "numerical_features": features_numerical,
            "categorical_options": categorical_options,
            "artifacts_status": {
                "model_pkl": os.path.exists(model_path),
                "preprocessor_pkl": os.path.exists(preprocessor_path),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/train")
def train_model():
    try:
        trainer = TrainPipeline()
        r2_score = trainer.run_pipeline()
        return {
            "status": "success",
            "message": "Model retraining pipeline completed successfully",
            "r2_score": round(float(r2_score), 4),
        }
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
