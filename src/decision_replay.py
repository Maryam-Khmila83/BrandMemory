try:
    from .retrieve import retrieve_decision_with_evidence
    from .evidence_quality import verify_claim
except ImportError:
    from retrieve import retrieve_decision_with_evidence
    from evidence_quality import verify_claim


import re

def extract_reasoning_claims(reasoning):
    """Extract individual bullet-point claims from decision reasoning."""

    return re.findall(
        r"^\s*[-*]\s+(.+)$",
        reasoning,
        flags=re.MULTILINE
    )

def extract_section(document_text, *section_titles):
    for section_title in section_titles:
        pattern = (
            rf"^##\s+{re.escape(section_title)}\s*$"
            rf"\s*\n(.*?)(?=^##\s+|\Z)"
        )
        match = re.search(
            pattern,
            document_text,
            flags=re.MULTILINE | re.DOTALL
        )
        if match:
            return match.group(1).strip()

    return "Section not found."



def analyze_experiment_results(later_outcomes):
    """
    Extract and summarize the experiment results document.
    """

    results_document = next(
        (
            document
            for document in later_outcomes
            if document["document_type"] == "experiment_results"
        ),
        None
    )

    if results_document is None:
        return None

    content = results_document["content"]

    return {
        "source": results_document["source"],
        "objective": extract_section(content, "1. Experiment objective"),
        "results": extract_section(content, "2. Recorded experiment results"),
        "comparison": extract_section(content, "3. Comparison"),
        "hypothesis_evaluation": extract_section(
            content, "4. Evaluation of the original hypothesis"
        ),
        "recommendation": extract_section(
            content, "5. Recommended next action"
        ),
        "lessons": extract_section(content, "6. Lessons learned"),
    }

def generate_answer(replay):
    details = replay["decision_details"]
    experiment = replay["experiment_analysis"]

    answer = f"""
FASHIONCO'S DECISION
{details["decision"]}

WHY WAS THIS DECISION MADE?
{details["context"]}

REASONING
{details["reasoning"]}

WHAT HAPPENED AFTERWARD?
"""

    if experiment:
        answer += f"""
Experiment results:
{experiment["comparison"]}

What did FashionCo learn?
{experiment["hypothesis_evaluation"]}

Recommended next step:
{experiment["recommendation"]}
"""
        answer += """Note: Experiment results are simulated for this portfolio demonstration.
They should not be interpreted as real company results."""
    else:
        answer += f"""
No linked experiment results were found.

Follow-up status:
{details["status"]}
"""

    return answer.strip()

def build_decision_replay(question):
    """
    Build a structured Decision Replay from retrieved documents.
    """

    decision, original_evidence, later_outcomes = (
        retrieve_decision_with_evidence(question)
    )

    if decision is None:
        return None

    decision_text = decision["content"]

    replay = {
        "question": question,
        "decision": decision,

        "decision_details": {
            "decision": extract_section(decision_text, "Decision"),
            "context": extract_section(
                decision_text, "Context and evidence", "Context"
            ),
            "alternatives": extract_section(
                decision_text, "Alternatives considered"
            ),
            "reasoning": extract_section(
                decision_text, "Reasoning", "Rationale"
            ),
            "risks": extract_section(
                decision_text, "Risks and limitations", "Limitations"
            ),
            "status": extract_section(
                decision_text, "Decision status", "Follow-up"
            ),
        },

        "original_evidence": original_evidence,
        "later_outcomes": later_outcomes,
    }
    replay["experiment_analysis"] = analyze_experiment_results(
        later_outcomes
    )

    # Verify individual reasoning claims against original evidence.
    claims = extract_reasoning_claims(
        replay["decision_details"]["reasoning"]
    )

    replay["claim_verification"] = [
        {
            "claim": claim,
            "evidence_checks": [
                {
                    "source": document["source"],
                    **verify_claim(claim, document)
                }
                for document in original_evidence
            ]
        }
        for claim in claims
    ]

    return replay


