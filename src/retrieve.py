
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import re
import calendar

# 1. Locate the project directory
project_dir = Path(__file__).resolve().parents[1]

# 2. Locate the Chroma database
db_path = project_dir / "chroma_db"

# 3. Connect to the persistent database
client = chromadb.PersistentClient(path=str(db_path))

# 4. Access the existing collection
collection = client.get_collection(name="brandmemory")

# 5. Load the same embedding model used during indexing
embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# 6. Define the retrieval function

def retrieve_documents(question, top_k=5, filters=None):
    """
    Retrieve relevant chunks, optionally filtering by metadata.
    """

    query_embedding = embedding_model.encode(question)

    # Prepare the search parameters
    search_parameters = {
        "query_embeddings": [query_embedding.tolist()],
        "n_results": min(top_k, collection.count()),
        "include": ["documents", "metadatas", "distances"]
    }

    # Apply metadata filters only when provided
    if filters:
        search_parameters["where"] = filters

    results = collection.query(**search_parameters)

    retrieved_documents = []

    for i in range(len(results["documents"][0])):
        retrieved_documents.append({
            "content": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    
    # Keep only the closest matching chunk from each source report
    best_by_source = {}

    for document in retrieved_documents:
        source = document["source"]

        if (
            source not in best_by_source
            or document["distance"] < best_by_source[source]["distance"]
        ):
            best_by_source[source] = document

    return list(best_by_source.values())



def get_full_document(source):
    """Retrieve and combine ordered chunks from one source file."""

    results = collection.get(
        where={"source": source},
        include=["documents", "metadatas"]
    )

    ordered_chunks = sorted(
        zip(results["ids"], results["documents"]),
        key=lambda item: int(item[0].rsplit("__chunk_", 1)[1])
    )

    if not ordered_chunks:
        return ""

    full_text = ordered_chunks[0][1]

    for _, chunk in ordered_chunks[1:]:
        # Find the largest overlap between the assembled text
        # and the next chunk, then append only new content.
        max_overlap = min(len(full_text), len(chunk))
        overlap = 0

        for size in range(max_overlap, 0, -1):
            if full_text.endswith(chunk[:size]):
                overlap = size
                break

        new_text = chunk[overlap:]
        if new_text:
            if full_text and not full_text.endswith(("\n", " ")):
                full_text += "\n"
            full_text += new_text

    return full_text


def detect_document_types(question):
    """
    Identify document types relevant to a question.
    A question can require multiple document types.
    """

    question = question.lower()
    document_types = []

    # 1. Decisions
    if any(word in question for word in [
        "decision", "decide", "why", "pause", "scale",
        "stop", "approved"
    ]):
        document_types.append("decision")

    # 2. Regular campaign performance reports
    if (
        "campaign" in question
        and any(word in question for word in [
            "results", "performance", "roas",
            "conversions", "revenue", "spend"
        ])
    ):
        document_types.append("campaign_report")

    # Student targeting decisions also need the student campaign report
    if "student" in question:
        document_types.append("campaign_report")

    # Summer campaign decisions may need their original brief and performance
    # brief and performance report.
    if (
        "summer campaign" in question
        and any(word in question for word in [
            "why", "decision", "decide", "scale", "stop"
        ])
    ):
        document_types.extend([
            "campaign_report",
            "campaign_brief"
        ])

    # 3. Experiment plans
    if (
        "hypothesis" in question
        or "experiment plan" in question
        or "test plan" in question
        or (
            "experiment" in question
            and any(word in question for word in [
                "proposed", "budget", "design"
            ])
        )
    ):
        document_types.append("experiment_plan")

    # 4. Experiment results
    if (
        "experiment results" in question
        or "experiment outcome" in question
        or (
            "experiment" in question
            and any(word in question for word in [
                "compare", "comparison", "variant",
                "control", "product-focused", "outcome"
            ])
        )
    ):
        document_types.append("experiment_results")

    # 5. Campaign briefs
    if any(word in question for word in [
        "brief", "objective", "original objective",
        "target audience", "campaign goal"
    ]):
        document_types.append("campaign_brief")

    # 6. Meeting notes
    if any(word in question for word in [
        "meeting", "discussed", "discussion",
        "alternatives"
    ]):
        document_types.append("meeting_note")

    # Remove duplicate types while preserving order
    return list(dict.fromkeys(document_types))

def extract_metadata_filters(question):
    """
    Extract structured campaign information from a question.
    """

    question = question.lower()
    filters = {}

    # Extract campaign theme
    theme_values = {
        "brand story": "Brand Story",
        "product launch": "Product Launch",
        "influencer": "Influencer",
        "promo": "Promo",
        "educational": "Educational",
        "ugc": "UGC",
        "retargeting": "Retargeting",
        "seasonal": "Seasonal",
        "student": "Student"
    }

    for theme, stored_value in theme_values.items():
        if theme in question:
            filters["theme"] = stored_value
            break

    # Extract advertising platform
    platforms = [
        "Google Search",
        "Google Display",
        "LinkedIn",
        "TikTok",
        "Meta",
        "Snapchat"
    ]

    for platform in platforms:
        if platform.lower() in question:
            filters["platform"] = platform
            break

    # Extract month and year
    year_match = re.search(r"\b(20\d{2})\b", question)

    month_number = None

    for month_number_candidate in range(1, 13):
        month_name = calendar.month_name[month_number_candidate].lower()

        if month_name in question:
            month_number = month_number_candidate
            break

    if year_match and month_number:
        year = year_match.group(1)

        filters["month"] = (
            f"{year}-{month_number:02d}"
        )

    return filters

def is_year_available(year):
    """
    Check whether the knowledge base contains documents
    for the requested year.
    """

    results = collection.get(
        where={"year": year},
        include=["metadatas"]
    )

    return len(results["metadatas"]) > 0

def retrieve_relevant_documents(question, top_k=5):
    """
    Retrieve relevant documents and reconstruct their full content.
    """

    # 1. Identify relevant document types
    document_types = detect_document_types(question)

    metadata_filters = extract_metadata_filters(question)

    requested_year = re.search(r"\b(20\d{2})\b", question)

    if requested_year:
        year = requested_year.group(1)

        if not is_year_available(year):
            print(
                f"No documents found for the requested year: {year}"
            )
            return []

    # 2. Retrieve relevant chunks
    if not document_types:
        retrieved_documents = retrieve_documents(
            question,
            top_k=top_k
        )

    else:
        retrieved_documents = []

        for document_type in document_types:

            where_conditions = [
                {"document_type": {"$eq": document_type}}
            ]

            for key, value in metadata_filters.items():
                where_conditions.append({
                    key: {"$eq": value}
                })

            filters = (
                {"$and": where_conditions}
                if len(where_conditions) > 1
                else where_conditions[0]
            )

            results = retrieve_documents(
                question,
                top_k=top_k,
                filters=filters
            )

            # Fallback if exact metadata filtering finds nothing
            if not results and metadata_filters:
                results = retrieve_documents(
                    question,
                    top_k=top_k,
                    filters={"document_type": document_type}
                )

            retrieved_documents.extend(results)

    # 3. Keep the best matching chunk from each source
    best_by_source = {}

    for document in retrieved_documents:
        source = document["source"]

        if (
            source not in best_by_source
            or document["distance"] < best_by_source[source]["distance"]
        ):
            best_by_source[source] = document

    # 4. Sort documents by relevance
    final_results = sorted(
        best_by_source.values(),
        key=lambda document: document["distance"]
    )[:top_k]

    # 5. Preserve the original retrieved chunk and reconstruct the full document
    for document in final_results:
        document["matched_chunk"] = document["content"]
        document["content"] = get_full_document(document["source"])

    return final_results


def retrieve_decision_with_evidence(question):
    """Retrieve a decision, its original evidence, and later outcomes."""


    id_pattern = (
        r"BRIEF-\d{4}-\d{3}"
        r"|MEETING-\d{4}-\d{3}"
        r"|DECISION-\d{4}-\d{3}"
        r"|DEC-\d{3}"
        r"|REPORT-[A-Z]+-\d{4}-\d{3}"
        r"|EXPERIMENT-RESULTS-\d{4}-\d{3}"
        r"|EXPERIMENT-\d{4}-\d{3}"
    )

    # 1. Find the relevant decision.
    decisions = retrieve_documents(
        question,
        top_k=10,
        filters={"document_type": "decision"}
    )

    if not decisions:
        return None, [], []

    decision = decisions[0]
    full_decision = get_full_document(decision["source"])
    decision["content"] = full_decision

    # 2. Extract the decision ID, if available.
    decision_match = re.search(
        rf"\*\*Decision ID:\*\*\s*({id_pattern})"
        rf"|\*\*Document ID:\*\*\s*({id_pattern})",
        full_decision
    )

    decision_id = None

    if decision_match:
        decision_id = next(
            (group for group in decision_match.groups() if group),
            None
        )

    # 3. Find documents referenced by ID.
    related_ids = set(re.findall(id_pattern, full_decision))

    if decision_id:
        related_ids.discard(decision_id)

    # 4. Load all indexed documents.
    all_results = collection.get(include=["metadatas"])

    source_types = {}

    for metadata in all_results["metadatas"]:
        source_types[metadata["source"]] = metadata.get(
            "document_type", "general"
        )

    documents_by_id = {}
    documents_by_source = {}
    document_references = {}

    for source, document_type in source_types.items():

        content = get_full_document(source)

        document = {
            "source": source,
            "content": content,
            "document_type": document_type
        }

        documents_by_source[source] = document

        id_match = re.search(
            rf"\*\*(?:Document ID|Decision ID):\*\*\s*({id_pattern})",
            content
        )

        if id_match:
            document_id = id_match.group(1)
            document["document_id"] = document_id

            documents_by_id[document_id] = document

            document_references[document_id] = set(
                re.findall(id_pattern, content)
            )

    # 5. Find original evidence using referenced filenames.
    original_evidence = []

    referenced_files = re.findall(
        r"`([^`]+\.md)`",
        full_decision
    )

    for filename in referenced_files:
        document = documents_by_source.get(filename)

        if document:
            original_evidence.append(document)

    # Also support evidence linked through document IDs.
    for document_id in related_ids:
        document = documents_by_id.get(document_id)

        if document and document not in original_evidence:
            original_evidence.append(document)

    # 6. Find later experiment plans linked to the decision.
    later_outcomes = []
    experiment_plan_ids = set()

    if decision_id:
        for document_id, document in documents_by_id.items():

            if (
                document["document_type"] == "experiment_plan"
                and decision_id in document_references[document_id]
            ):
                later_outcomes.append(document)
                experiment_plan_ids.add(document_id)

    # 7. Find experiment results linked to the decision or plans.
    for document_id, document in documents_by_id.items():

        if document["document_type"] != "experiment_results":
            continue

        references = document_references[document_id]

        if (
            decision_id and decision_id in references
        ) or references.intersection(experiment_plan_ids):

            if document not in later_outcomes:
                later_outcomes.append(document)

    return decision, original_evidence, later_outcomes

