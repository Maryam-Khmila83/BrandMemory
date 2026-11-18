try:
    from .retrieve import retrieve_relevant_documents
    from .campaign_analytics import get_theme_performance_summary
except ImportError:
    from retrieve import retrieve_relevant_documents
    from campaign_analytics import get_theme_performance_summary
import re
import requests


def get_analytics_context(question):
    months = {
        "january": "Jan", "february": "Feb",
        "march": "Mar", "april": "Apr",
        "may": "May", "june": "Jun",
        "july": "Jul", "august": "Aug",
        "september": "Sep", "october": "Oct",
        "november": "Nov", "december": "Dec"
    }

    match = re.search(
        r"\b(" + "|".join(months) + r")\s+(20\d{2})\b",
        question.lower()
    )

    if not match:
        return None

    month = months[match.group(1)]
    year = match.group(2)

    summary = get_theme_performance_summary(year, month)

    return (
        "SOURCE: data/processed/campaign_summary.csv\n"
        "Calculated analytics from simulated demo data:\n\n"
        + summary
    )


def build_context(question, top_k=3):
    """
    Retrieve relevant documents and prepare their content
    as context for answer generation.
    """
    documents = retrieve_relevant_documents(
        question,
        top_k=top_k
    )

    if not documents:
        return None, []

    context = ""

    for document in documents:
        context += f"\nSOURCE: {document['source']}\n"
        context += document["content"]
        context += "\n" + "-" * 50 + "\n"

    return context, documents



def detect_question_type(question):
    """
    Identify the type of information requested by the user.
    """

    question = question.lower()

    if any(word in question for word in [
        "experiment", "reveal", "hypothesis", "product-focused"
    ]):
        return "experiment"

    elif any(word in question for word in [
        "decide", "decision", "scale", "stop", "why"
    ]):
        return "decision"

    elif any(word in question for word in [
        "objective", "goal", "target audience", "purpose"
    ]):
        return "campaign_objective"

    elif any(word in question for word in [
        "meeting", "discussed", "discussion"
    ]):
        return "meeting"

    elif any(word in question for word in [
        "roas", "conversions", "revenue", "spend", "performance"
    ]):
        return "performance"

    return "general"


def extract_section(context, section_title):
    """
    Extract a specific Markdown section from the retrieved context.
    """

    pattern = rf"## {re.escape(section_title)}\s*(.*?)(?=\n## |\Z)"

    match = re.search(pattern, context, re.DOTALL)

    if match:
        return match.group(1).strip()

    return ""

def generate_answer(question, context, analytics_context=None):
    if not context and not analytics_context:

        return "I couldn't find relevant information to answer this question."

    prompt = f"""
You are BrandMemory, an AI assistant for a fictional fashion company called FashionCo.

Your task is to answer the user's question using ONLY the information
provided in the retrieved documents.

Instructions:
1. Answer the user's question directly and clearly.
2. Do not invent facts or information.
3. If the documents do not contain the answer, say so.
4. Distinguish recorded facts from assumptions and recommendations.
5. Mention the source filenames that support your answer.
6. If the information is simulated, explicitly mention that it is simulated.
7. If documents contain conflicting information, point out the conflict.

Retrieved documents:

{context or "No relevant documents retrieved."}

Calculated business analytics:

{analytics_context or "No analytics data available for this question."}

User question:
{question}

Your answer:
"""

    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    response = requests.post(
        url,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    return result["response"].strip()

