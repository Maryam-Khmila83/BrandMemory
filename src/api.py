
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

from src.campaign_analytics import (
    load_fashionco_data,
    analyze_by_theme,
    analyze_by_platform,
    analyze_platform_by_objective,
    analyze_monthly_trends,
)

from pydantic import BaseModel
from src.answer import (
    build_context,
    get_analytics_context,
    generate_answer as generate_assistant_answer,
)

from src.decision_replay import (
    build_decision_replay,
    generate_answer as generate_decision_replay_answer,
)

from src.evidence_quality import assess_evidence_documents

from fastapi.responses import FileResponse
from src.report_generator import generate_marketing_report

# Create the API
app = FastAPI(title="BrandMemory API")

# Allow React to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load campaign data
def get_campaign_data():
    return load_fashionco_data()


# Convert Pandas DataFrames into JSON-compatible data
def dataframe_to_json(df):
    return json.loads(df.to_json(orient="records"))


# Basic API test
@app.get("/")
def home():
    return {
        "message": "Welcome to BrandMemory API",
        "status": "running"
    }


# Dashboard KPIs
@app.get("/api/dashboard")
def get_dashboard():
    df = get_campaign_data()

    theme_results = analyze_by_theme(df)

    top_theme = theme_results.iloc[0]

    first_date = df["first_date"].min()
    last_date = df["last_date"].max()

    return {
        "campaign_groups": int(len(df)),
        "campaign_themes": int(df["theme"].nunique()),
        "top_theme": str(top_theme["theme"]),
        "top_theme_roas": round(float(top_theme["roas"]), 2),
        "reporting_period": {
            "start": str(first_date),
            "end": str(last_date)
        }
    }


# Performance by theme
@app.get("/api/analytics/themes")
def get_theme_analytics():
    df = get_campaign_data()

    results = analyze_by_theme(df)

    return dataframe_to_json(results)


# Performance by platform
@app.get("/api/analytics/platforms")
def get_platform_analytics():
    df = get_campaign_data()

    results = analyze_by_platform(df)

    return dataframe_to_json(results)


# Platform performance by campaign objective
@app.get("/api/analytics/platform-objectives")
def get_platform_objective_analytics():
    df = get_campaign_data()

    results = analyze_platform_by_objective(df)

    return dataframe_to_json(results)


# Monthly performance trends
@app.get("/api/analytics/monthly")
def get_monthly_analytics():
    df = get_campaign_data()

    results = analyze_monthly_trends(df)

    return dataframe_to_json(results)


# =====================================
# AI ASSISTANT
# =====================================

class ChatRequest(BaseModel):
    question: str


@app.post("/api/assistant/chat")
def chat_with_assistant(request: ChatRequest):

    question = request.question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    # Retrieve relevant documents
    context, documents = build_context(
        question,
        top_k=3
    )

    # Retrieve calculated analytics if relevant
    analytics_context = get_analytics_context(question)

    # Generate the AI answer
    answer = generate_assistant_answer(
        question,
        context,
        analytics_context
    )

    # Prepare source information
    sources = []

    for document in documents:
        sources.append({
            "name": document["source"],
            "distance": round(
                float(document["distance"]), 4
            )
        })

    if analytics_context:
        sources.append({
            "name": "campaign_summary.csv",
            "type": "Calculated analytics"
        })

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }

# =====================================
# DECISION REPLAY
# =====================================

class DecisionReplayRequest(BaseModel):
    question: str


@app.post("/api/decision-replay")
def decision_replay_endpoint(request: DecisionReplayRequest):

    question = request.question.strip()

    if not question:
        return {
            "error": "Please enter a question."
        }

    # Build the decision replay
    replay = build_decision_replay(question)

    if replay is None:
        return {
            "found": False,
            "message": "No relevant decision was found.",
        }

    # Assess original evidence quality
    evidence_assessments = assess_evidence_documents(
        replay["original_evidence"]
    )

    # Generate the replay explanation
    answer = generate_decision_replay_answer(replay)

    return {
        "found": True,
        "question": replay["question"],
        "answer": answer,

        "decision": {
            "source": replay["decision"]["source"],
            **replay["decision_details"],
        },

        "evidence": evidence_assessments,

        "claim_verification": replay["claim_verification"],

        "later_outcomes": [
            {
                "source": document["source"],
                "document_type": document["document_type"],
            }
            for document in replay["later_outcomes"]
        ],

        "experiment_analysis": replay["experiment_analysis"],
    }

@app.post("/api/reports/generate")
def generate_report():
    try:
        report_path = generate_marketing_report()

        return FileResponse(
            path=report_path,
            media_type="application/pdf",
            filename=report_path.name,
        )

    except Exception as e:
        return {
            "error": str(e)
        }