from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


def build_index_data():
    # 1. Locate the BrandMemory project folder
    project_dir = Path(__file__).resolve().parents[1]

    # 2. Locate the folder containing our Markdown documents
    documents_dir = project_dir / "data" / "documents"

    # 3. Load all Markdown files
    markdown_files = list(documents_dir.glob("*.md"))

    documents = []
    for file_path in markdown_files:
        documents.append({
            "source": file_path.name,
            "content": file_path.read_text(encoding="utf-8")
        })

    # 4. Convert dictionaries into LangChain Documents
    langchain_documents = []
    for doc in documents:
        langchain_documents.append(
            Document(
                page_content=doc["content"],
                metadata={"source": doc["source"]}
            )
        )

    # 5. Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120
    )

    chunks = text_splitter.split_documents(langchain_documents)

    # 6. Load the embedding model
    embedding_model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # 7. Generate embeddings for every chunk
    chunk_texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_model.encode(chunk_texts)

    # 8. Return both results
    return chunks, embeddings


# Run this block only when executing this file directly
#if __name__ == "__main__":
 #   chunks, embeddings = build_index_data()

  #  print("Number of chunks:", len(chunks))
   # print("Embeddings shape:", embeddings.shape)

if __name__ == "__main__":
    chunks, embeddings = build_index_data()

    print("Number of chunks:", len(chunks))
    print("Embeddings shape:", embeddings.shape)

    print("\nSample chunk:")
    print(chunks[0].page_content)

    print("\nMetadata:")
    print(chunks[0].metadata)