"""
Vector Store Manager
Manages ChromaDB collections for storing and retrieving video transcript embeddings.
"""

import logging
from typing import List, Optional

import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level ChromaDB client (singleton)
_chroma_client: Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create the ChromaDB persistent client."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR
        )
        logger.info(f"ChromaDB client initialized at: {settings.CHROMA_PERSIST_DIR}")
    return _chroma_client


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Create a Gemini embeddings instance."""
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
    )


def get_collection_name(video_id: str) -> str:
    """Generate a collection name for a video. ChromaDB collection names must be 3-63 chars."""
    name = f"vid_{video_id}"
    # ChromaDB collection names: 3-63 chars, alphanumeric + underscores/hyphens
    return name[:63]


async def create_vector_store(
    video_id: str,
    transcript_text: str,
    segments: list,
) -> int:
    """
    Chunk the transcript, generate embeddings, and store in ChromaDB.
    
    Args:
        video_id: The YouTube video ID
        transcript_text: The full transcript text
        segments: The transcript segments with timestamps
        
    Returns:
        Number of chunks created
    """
    logger.info(f"Creating vector store for video: {video_id}")

    # Split transcript into chunks with timestamp metadata
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    # Create documents with timestamp metadata
    documents = []
    chunks = splitter.split_text(transcript_text)

    for i, chunk_text in enumerate(chunks):
        # Find the approximate timestamp for this chunk
        timestamp = _find_timestamp_for_chunk(chunk_text, segments)
        doc = Document(
            page_content=chunk_text,
            metadata={
                "video_id": video_id,
                "chunk_index": i,
                "timestamp": timestamp,
            }
        )
        documents.append(doc)

    # Create embeddings and store in ChromaDB
    embeddings = get_embeddings()
    collection_name = get_collection_name(video_id)

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name,
        client=get_chroma_client(),
    )

    logger.info(f"Vector store created: {len(documents)} chunks for video {video_id}")
    return len(documents)


def get_retriever(video_id: str, k: int = None):
    """
    Get a retriever for a specific video's vector store.
    
    Args:
        video_id: The YouTube video ID
        k: Number of documents to retrieve (default from settings)
        
    Returns:
        A LangChain retriever instance
    """
    if k is None:
        k = settings.RETRIEVER_K

    embeddings = get_embeddings()
    collection_name = get_collection_name(video_id)

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        client=get_chroma_client(),
    )

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )


async def delete_vector_store(video_id: str) -> bool:
    """Delete the vector store collection for a video."""
    try:
        collection_name = get_collection_name(video_id)
        client = get_chroma_client()
        client.delete_collection(collection_name)
        logger.info(f"Deleted vector store for video: {video_id}")
        return True
    except Exception as e:
        logger.warning(f"Could not delete vector store for {video_id}: {e}")
        return False


def _find_timestamp_for_chunk(chunk_text: str, segments: list) -> str:
    """
    Find the approximate timestamp for a text chunk by matching
    against the transcript segments.
    """
    if not segments:
        return "0:00"

    # Find the segment that best matches the start of the chunk
    chunk_start = chunk_text[:50].lower()
    best_match_idx = 0
    best_score = 0

    for i, segment in enumerate(segments):
        seg_text = segment["text"].lower()
        # Simple overlap scoring
        if seg_text in chunk_start or chunk_start in seg_text:
            return segment.get("timestamp", "0:00")
        # Count common words
        chunk_words = set(chunk_start.split())
        seg_words = set(seg_text.split())
        score = len(chunk_words & seg_words)
        if score > best_score:
            best_score = score
            best_match_idx = i

    return segments[best_match_idx].get("timestamp", "0:00")
