
import re

def extract_metric_value(content, metric_name):
    """
    Extract a numeric value from a Markdown metrics table.
    Supports indentation before table rows.
    """

    pattern = (
        rf"^[ \t]*\|[ \t]*{re.escape(metric_name)}[ \t]*"
        rf"\|[ \t]*([\d,]+(?:\.\d+)?)[ \t]*\|"
    )

    match = re.search(pattern, content, flags=re.MULTILINE)

    if match:
        return float(match.group(1).replace(",", ""))

    return None


def assess_evidence(document):
    """
    Assess the strength and limitations of one evidence document.

    This is an initial rule-based assessment, not a
    complete semantic fact-verification system.
    """

    content = document["content"]
    source = document["source"]
    text = content.lower()

    assessment = {
        "source": source,
        "classification": "Contextual evidence",
        "supports": [],
        "limitations": [],
        "data_status": "Not specified"
    }
    has_metric_inconsistency = False

    # 1. Identify synthetic data.
    if any(term in text for term in [
        "synthetic demonstration data",
        "fictional data",
        "simulated data"
    ]):
        assessment["data_status"] = "Synthetic / simulated"

    # 2. Extract and compare recorded campaign metrics.

    spend = extract_metric_value(content, "Advertising spend")
    revenue = extract_metric_value(content, "Recorded revenue")
    actual_roas = extract_metric_value(content, "ROAS")
    target_roas = extract_metric_value(
        content, "Team's target ROAS"
    )

    if actual_roas is not None and target_roas is not None:

        assessment["classification"] = (
            "Direct support for recorded performance"
        )

        assessment["supports"].append(
            f"Recorded ROAS: {actual_roas:.2f}"
        )

        assessment["supports"].append(
            f"Target ROAS: {target_roas:.2f}"
        )

        difference = actual_roas - target_roas

        if difference < 0:
            assessment["supports"].append(
                f"Recorded ROAS was {abs(difference):.2f} "
                "below the target."
            )

        elif difference > 0:
            assessment["supports"].append(
                f"Recorded ROAS exceeded the target by "
                f"{difference:.2f}."
            )

        else:
            assessment["supports"].append(
                "Recorded ROAS exactly met the target."
            )

    elif actual_roas is not None:
        assessment["classification"] = "Partial support"
        assessment["supports"].append(
            f"Recorded ROAS: {actual_roas:.2f}"
        )

    if spend is not None and revenue is not None:
        assessment["supports"].append(
            f"Recorded advertising spend: {spend:.2f}"
        )

        assessment["supports"].append(
            f"Recorded revenue: {revenue:.2f}"
        )

        if spend > 0:
            calculated_roas = revenue / spend

            assessment["supports"].append(
                f"Calculated ROAS from revenue and spend: "
                f"{calculated_roas:.2f}"
            )

            if actual_roas is not None:
                if abs(calculated_roas - actual_roas) > 0.01:

                    has_metric_inconsistency = True
                    assessment["limitations"].append(
                        f"ROAS inconsistency: reported ROAS is "
                        f"{actual_roas:.2f}, but calculated ROAS "
                        f"is {calculated_roas:.2f}."
                    )
                else:
                    assessment["supports"].append(
                        "Reported ROAS is consistent with "
                        "revenue divided by advertising spend."
                    )

    if "audience:" in text:
        assessment["supports"].append(
            "The document explicitly records an audience."
        )

    # 3. Identify explicit limitations.
    limitation_phrases = [
        "does not establish",
        "does not prove",
        "not proof",
        "must be verified",
        "not necessarily",
        "cannot conclude",
        "insufficient evidence"
    ]

    for phrase in limitation_phrases:
        if phrase in text:
            assessment["limitations"].append(
                f"The document states: '{phrase}'."
            )

    if has_metric_inconsistency:
        assessment["classification"] = (
            "Inconsistent numerical evidence"
        )

    # 4. Flag missing information.
    if not assessment["supports"]:
        assessment["limitations"].append(
            "No specific performance evidence was identified "
            "by the current assessment rules."
        )

    return assessment


def assess_evidence_documents(documents):
    """Assess a collection of evidence documents."""

    return [
        assess_evidence(document)
        for document in documents
    ]


def verify_claim(claim, document):
    """
    Check whether an individual claim is supported
    by a specific evidence document.

    This is a rule-based prototype, not an LLM fact checker.
    """

    content = document["content"].lower()
    claim_lower = claim.lower()

    result = {
        "claim": claim,
        "classification": "Unsupported",
        "reason": "The available evidence does not establish this claim."
    }

    # 1. Detect causal claims.
    causal_terms = [
        "caused",
        "because of",
        "due to",
        "resulted from",
        "led to"
    ]

    if any(term in claim_lower for term in causal_terms):
        result["reason"] = (
            "The evidence does not establish a causal relationship."
        )
        return result

    # 2. Verify a claim about ROAS being below target.
    if any(term in claim_lower for term in [
        "roas",
        "return-on-ad-spend",
        "return on ad spend"
    ]) and any(term in claim_lower for term in [
        "below target",
        "below the target",
        "did not meet",
        "underperformed"
    ]):

        actual_roas = extract_metric_value(
            document["content"], "ROAS"
        )

        target_roas = extract_metric_value(
            document["content"], "Team's target ROAS"
        )

        if actual_roas is not None and target_roas is not None:

            if actual_roas < target_roas:
                result["classification"] = "Directly supported"
                result["reason"] = (
                    f"Recorded ROAS ({actual_roas:.2f}) "
                    f"was below the target ({target_roas:.2f})."
                )

            else:
                result["reason"] = (
                    f"Recorded ROAS ({actual_roas:.2f}) "
                    f"was not below the target ({target_roas:.2f})."
                )

        return result

    # 3. Verify whether the report records the audience.
    if "audience" in claim_lower or "students" in claim_lower:

        if "audience:" in content and "student" in content:
            result["classification"] = "Directly supported"
            result["reason"] = (
                "The report explicitly records a student audience."
            )

        return result

    return result

