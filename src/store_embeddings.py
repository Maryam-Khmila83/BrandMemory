from pathlib import Path
import chromadb
from load_documents import build_index_data
import re
chunks, embeddings = build_index_data()


def extract_campaign_metadata(chunk):
    metadata = dict(chunk.metadata)

    # Find the Campaign group line in the report
    match = re.search(
        r"\*\*Campaign group:\*\*\s*(.+)",
        chunk.page_content
    )

    if match:
        campaign_group = match.group(1).strip()
        parts = campaign_group.split("_")

        # Expected ending: platform_month_year
        # Example: ..._Google Search_Nov_2024
        if len(parts) >= 2:
            year = parts[-1]
            month = parts[-2]

            month_names = {
                "Jan": "01", "Feb": "02", "Mar": "03",
                "Apr": "04", "May": "05", "Jun": "06",
                "Jul": "07", "Aug": "08", "Sep": "09",
                "Oct": "10", "Nov": "11", "Dec": "12"
            }

            if month in month_names and year.isdigit():
                metadata["month"] = f"{year}-{month_names[month]}"
                metadata["year"] = year

                # The platform is everything between the
                # objective and the month/year suffix.
                metadata["platform"] = parts[-3] if len(parts) >= 3 else ""

                # Google Search contains a space, so recover it
                # from the full campaign group.
                platform_match = re.search(
                    r"_(Google Search|Google Display|Meta|TikTok|LinkedIn|Snapchat)_"
                    + re.escape(month)
                    + r"_"
                    + re.escape(year)
                    + r"$",
                    campaign_group
                )

                if platform_match:
                    metadata["platform"] = platform_match.group(1)

        # Extract the theme from the campaign group.
        # The theme is the segment immediately after the account.
        if len(parts) >= 5:
            metadata["theme"] = parts[2]

    return metadata



def extract_document_type(chunk):
    content = chunk.page_content.lower()
    source = chunk.metadata.get("source", "").lower()
    filename = Path(source).stem.lower()

    # Decisions
    if (
        "decision" in filename
        or re.search(
            r"\*\*document type:\*\*\s*"
            r"(?:marketing decision|decision memo|decision record)\b",
            content,
        )
    ):
        return "decision"

    # Experiment results
    if (
        "experiment_results" in filename
        or "**document type:** experiment results" in content
    ):
        return "experiment_results"

    # Experiment plans
    if (
        "experiment_plan" in filename
        or "**document type:** experiment plan" in content
    ):
        return "experiment_plan"

    # Campaign briefs — check before campaign reports
    if (
        "brief" in filename
        or "**document type:** campaign brief" in content
    ):
        return "campaign_brief"

    # Campaign performance reports
    if (
        "fashionco_campaign_" in filename
        or "fashionco_student_campaign" in filename
        or filename == "fashionco_summer_campaign_performance"
    ):
        return "campaign_report"

    # Meeting notes
    if (
        "meeting" in filename
        or "**document type:** meeting notes" in content
        or "**document type:** meeting note" in content
    ):
        return "meeting_note"

    return "general"


project_dir = Path(__file__).resolve().parents[1]
db_path = project_dir / "chroma_db"

# 1. Create a local ChromaDB database
client = chromadb.PersistentClient(path=str(db_path))

# 2. Create or retrieve our collection
collection = client.get_or_create_collection(
    name="brandmemory"
)
# Delete all existing records before re_indexing
exicsting_ids = collection.get(
    include=[]
)["ids"]

if exicsting_ids:
    collection.delete(ids=exicsting_ids)



# Build a metadata lookup for each document
source_metadata = {}

for chunk in chunks:
    metadata = extract_campaign_metadata(chunk)
    metadata["document_type"] = extract_document_type(chunk)

    source = metadata["source"]

    # Preserve metadata for campaign reports AND decision documents.
    # Keep the first metadata entry found for each source.
    if source not in source_metadata:
        source_metadata[source] = metadata

# 3. Store the chunks, embeddings, and source metadata
collection.upsert(
    ids=[
        f"{chunk.metadata['source']}__chunk_{i}"
        for i, chunk in enumerate(chunks)
    ],
    documents=[chunk.page_content for chunk in chunks],
    embeddings=embeddings.tolist(),
    metadatas=[
        {
            **chunk.metadata,
            **source_metadata.get(chunk.metadata["source"], {})
        }
        for chunk in chunks
    ]
)


# 4. Verify the stored data
print("Number of stored chunks:", collection.count())

# 5. Verify metadata for the new documents
sources_to_check = [
    "decision_001_pause_student_targeting.md",
    "fashionco_student_campaign_2025_01.md",
    "fashionco_summer_campaign_decision.md",
    "fashionco_summer_campaign_brief.md",
    "fashionco_summer_campaign_meeting.md",
    "fashionco_summer_campaign_performance.md",
    "fashionco_summer_campaign_experiment_plan.md",
    "fashionco_summer_campaign_experiment_results.md",
]

print("\n--- Metadata verification ---")

for source in sources_to_check:
    results = collection.get(
        where={"source": source},
        include=["documents", "metadatas"]
    )

    print(f"\nSource: {source}")
    print("Number of chunks:", len(results["ids"]))

    for metadata in results["metadatas"]:
        print(metadata)
