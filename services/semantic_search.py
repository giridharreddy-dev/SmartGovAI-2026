import json
import logging
import os

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, ".chroma_db")
SCHEMES_DIR = os.path.join(BASE_DIR, "data")

# ChromaDB is optional during test collection and in environments where the
# vector-search dependency is not installed. The API will return a controlled
# error instead of making the whole application fail to import.
try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    chromadb = None
    embedding_functions = None
    logger.warning("ChromaDB is not installed; semantic search is unavailable.")

collection = None

if chromadb is not None:
    try:
        chroma_client = chromadb.PersistentClient(path=DB_DIR)
        sentence_transformer_ef = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )
        collection = chroma_client.get_or_create_collection(
            name="health_schemes",
            embedding_function=sentence_transformer_ef,
        )
    except Exception:
        logger.exception("Failed to initialize ChromaDB")


def index_schemes():
    """Read JSON scheme files and index them into ChromaDB."""
    if collection is None:
        logger.error("ChromaDB collection is not initialized. Cannot index schemes.")
        return

    logger.info("Starting semantic indexing of schemes...")
    documents = []
    metadatas = []
    ids = []

    for filename in sorted(os.listdir(SCHEMES_DIR)):
        if not filename.endswith(".json") or filename in {"scheme_schema.json", "facilities.json"}:
            continue

        filepath = os.path.join(SCHEMES_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                for name, details in data.items():
                    details = details if isinstance(details, dict) else {}
                    simplified = details.get("simplified", {})
                    simplified = simplified if isinstance(simplified, dict) else {}
                    documents.append(
                        f"Title: {name}\nCategory: {details.get('category', '')}\n"
                        f"Description: {simplified.get('description', '')}\n"
                        f"Benefits: {simplified.get('benefits', '')}"
                    )
                    metadatas.append({
                        "source": filename,
                        "scheme_name": name,
                        "category": details.get("category", ""),
                    })
                    ids.append(name.replace(" ", "_"))
            elif isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict) or not item.get("title"):
                        continue
                    name = item["title"]
                    tags = item.get("tags", [])
                    tags = ", ".join(tags) if isinstance(tags, list) else tags
                    documents.append(
                        f"Title: {name}\nTags: {tags}\nDescription: {item.get('description', '')}"
                    )
                    metadatas.append({
                        "source": filename,
                        "scheme_name": name,
                        "link": item.get("link", ""),
                        "category": "Health & Wellness",
                    })
                    ids.append(name.replace(" ", "_"))
        except Exception:
            logger.exception("Error indexing %s", filename)

    if documents:
        try:
            collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
            logger.info("Successfully indexed %d schemes for semantic search.", len(documents))
        except Exception:
            logger.exception("Error during ChromaDB upsert")


def semantic_search(query: str, top_k: int = 5):
    """Search the vector database for schemes matching *query*."""
    if collection is None:
        return {"status": "error", "message": "Search engine not initialized."}

    try:
        results = collection.query(query_texts=[query], n_results=top_k)
        matches = []
        if results and results.get("ids") and results["ids"]:
            for i, result_id in enumerate(results["ids"][0]):
                metadata = (results.get("metadatas") or [[{}]])[0][i] or {}
                matches.append({
                    "id": result_id,
                    "scheme_name": metadata.get("scheme_name", ""),
                    "category": metadata.get("category", ""),
                    "distance": (results.get("distances") or [[0.0]])[0][i],
                    "document": (results.get("documents") or [[""]])[0][i],
                })
        return {"status": "success", "results": matches}
    except Exception as exc:
        logger.exception("Semantic search failed for query %r", query)
        return {"status": "error", "message": str(exc)}
