import os
import json
import logging
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, '.chroma_db')
SCHEMES_DIR = os.path.join(BASE_DIR, 'data')

# Initialize ChromaDB client
try:
    chroma_client = chromadb.PersistentClient(path=DB_DIR)
    
    # We use the default SentenceTransformer embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Get or create the collection
    collection = chroma_client.get_or_create_collection(
        name="health_schemes", 
        embedding_function=sentence_transformer_ef
    )
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {e}")
    collection = None

def index_schemes():
    """
    Reads all JSON files in the data directory and indexes them into ChromaDB.
    """
    if not collection:
        logger.error("ChromaDB collection is not initialized. Cannot index schemes.")
        return

    logger.info("Starting semantic indexing of schemes...")
    
    documents = []
    metadatas = []
    ids = []
    
    for filename in sorted(os.listdir(SCHEMES_DIR)):
        if filename.endswith(".json") and filename not in {"scheme_schema.json", "facilities.json"}:
            filepath = os.path.join(SCHEMES_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Depending on the format of the JSON (list vs dict)
                    if isinstance(data, dict):
                        # The national_and_ap_schemes.json format is a dict of {scheme_name: scheme_data}
                        for name, details in data.items():
                            doc_id = name.replace(" ", "_")
                            
                            # Create a rich text representation for the embedding
                            desc = details.get("simplified", {}).get("description", "")
                            benefits = details.get("simplified", {}).get("benefits", "")
                            category = details.get("category", "")
                            
                            doc_text = f"Title: {name}\nCategory: {category}\nDescription: {desc}\nBenefits: {benefits}"
                            
                            documents.append(doc_text)
                            metadatas.append({
                                "source": filename,
                                "scheme_name": name,
                                "category": category
                            })
                            ids.append(doc_id)
                            
                    elif isinstance(data, list):
                        # The new scraper format is a list of dicts
                        for item in data:
                            name = item.get("title", "")
                            if not name:
                                continue
                            doc_id = name.replace(" ", "_")
                            
                            desc = item.get("description", "")
                            tags = item.get("tags", [])
                            tags_str = ", ".join(tags) if isinstance(tags, list) else tags
                            
                            doc_text = f"Title: {name}\nTags: {tags_str}\nDescription: {desc}"
                            
                            documents.append(doc_text)
                            metadatas.append({
                                "source": filename,
                                "scheme_name": name,
                                "link": item.get("link", ""),
                                "category": "Health & Wellness"
                            })
                            ids.append(doc_id)
                            
            except Exception as e:
                logger.error(f"Error indexing {filename}: {e}")
                
    if documents:
        # Upsert into Chroma (updates existing, inserts new)
        try:
            # Chroma can process batches, let's do it in one go for now
            collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully indexed {len(documents)} schemes for semantic search.")
        except Exception as e:
            logger.error(f"Error during ChromaDB upsert: {e}")

def semantic_search(query: str, top_k: int = 5):
    """
    Searches the vector database for schemes conceptually matching the query.
    """
    if not collection:
        return {"status": "error", "message": "Search engine not initialized."}
        
    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        matches = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                matches.append({
                    "id": results["ids"][0][i],
                    "scheme_name": results["metadatas"][0][i].get("scheme_name", ""),
                    "category": results["metadatas"][0][i].get("category", ""),
                    "distance": results["distances"][0][i] if "distances" in results else 0.0,
                    "document": results["documents"][0][i] if "documents" in results else ""
                })
                
        return {"status": "success", "results": matches}
    except Exception as e:
        logger.error(f"Semantic search failed for query '{query}': {e}")
        return {"status": "error", "message": str(e)}
