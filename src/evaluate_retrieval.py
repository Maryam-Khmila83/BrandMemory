import json
from pathlib import Path

from retrieve import retrieve_relevant_documents


# 1. Locate the project and evaluation dataset

project_dir = Path(__file__).resolve().parents[1]
evaluation_file = project_dir / "data" / "evaluation_questions.json"

TOP_K = 5


# 2. Load evaluation questions

with open(evaluation_file, "r", encoding="utf-8") as file:
    evaluation_questions = json.load(file)


# 3. Evaluate retrieval

all_precisions = []
all_recalls = []

print("\nBRANDMEMORY RETRIEVAL EVALUATION")
print("=" * 65)

for item in evaluation_questions:

    question_id = item["id"]
    question = item["question"]
    expected_sources = set(item["expected_sources"])

    print(f"\nQUESTION {question_id}")
    print("-" * 65)
    print("Question:", question)

    # Retrieve the top 5 documents
    retrieved_documents = retrieve_relevant_documents(
        question,
        top_k=TOP_K
    )

    retrieved_sources = [
        document["source"]
        for document in retrieved_documents
    ]

    print("\nRetrieved sources:")

    for document in retrieved_documents:
        print(
            f" - {document['source']} "
            f"| distance: {document['distance']:.4f}"
        )
        print("   metadata:", document["metadata"])

    # 4. Handle questions with no expected source separately

    if not expected_sources:
        print("\nCASE: Negative retrieval test")
        print("Expected relevant sources: None")
        print(
            "Retrieved documents:",
            len(retrieved_sources)
        )
        print(
            "Note: The system currently always returns nearest "
            "matches, even when they are irrelevant."
        )
        continue

    # 5. Calculate Precision@5 and Recall@5

    relevant_retrieved = (
        set(retrieved_sources) & expected_sources
    )

    precision = len(relevant_retrieved) / TOP_K
    recall = len(relevant_retrieved) / len(expected_sources)

    all_precisions.append(precision)
    all_recalls.append(recall)

    print("\nExpected sources:")
    for source in sorted(expected_sources):
        print(" -", source)

    print("\nCorrectly retrieved:")
    for source in sorted(relevant_retrieved):
        print(" -", source)

    print(f"\nPrecision@{TOP_K}: {precision:.2f}")
    print(f"Recall@{TOP_K}:    {recall:.2f}")


# 6. Calculate average evaluation scores

print("\n\nFINAL EVALUATION RESULTS")
print("=" * 65)

if all_precisions:

    average_precision = sum(all_precisions) / len(all_precisions)
    average_recall = sum(all_recalls) / len(all_recalls)

    print(f"Evaluated positive questions: {len(all_precisions)}")
    print(f"Average Precision@{TOP_K}: {average_precision:.2f}")
    print(f"Average Recall@{TOP_K}:    {average_recall:.2f}")

else:
    print("No positive questions were evaluated.")

print("\nEvaluation completed.")