import logging
import os

from services.studio_catalog import CATALOG_PATH, load_legacy_catalog

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, ".chroma_db")

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
    """Index the legacy search subset of the master catalog."""
    if collection is None:
        logger.error("ChromaDB collection is not initialized. Cannot index schemes.")
        return

    logger.info("Starting semantic indexing of schemes...")
    documents = []
    metadatas = []
    ids = []

    for name, details in load_legacy_catalog(BASE_DIR).items():
        simplified = details.get("simplified") or {}
        documents.append(
            f"Title: {name}\nCategory: {details.get('category', '')}\n"
            f"Description: {simplified.get('description', '')}\n"
            f"Benefits: {simplified.get('benefits', '')}"
        )
        metadatas.append({
            "source": CATALOG_PATH.name,
            "scheme_name": name,
            "category": details.get("category", ""),
        })
        ids.append(name.replace(" ", "_"))

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
