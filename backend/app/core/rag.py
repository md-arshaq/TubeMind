"""
RAG Pipeline
The core Retrieval-Augmented Generation pipeline using LangChain + Gemini.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.core.vectorstore import get_retriever

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Response from the RAG pipeline."""
    answer: str
    sources: list  # List of {text, timestamp, score} dicts


# ──────────────────────────────────────────────
# Prompt Templates
# ──────────────────────────────────────────────

CHAT_PROMPT = PromptTemplate(
    template="""You are TubeMind, an intelligent AI assistant that helps users understand YouTube video content.
Answer the user's question ONLY based on the provided transcript context from the video.
If the context doesn't contain enough information to answer, say so honestly.
Be conversational, clear, and helpful. Use bullet points or numbered lists for complex answers.
When referencing specific parts of the video, mention approximate timestamps if available.

IMPORTANT FORMATTING RULES:
- Always use standard Markdown format.
- Leave a blank empty line before starting any bulleted or numbered lists.
- Add double newlines between paragraphs to make your answer highly readable with clear spacing.

TRANSCRIPT CONTEXT:
{context}

USER QUESTION: {question}

YOUR ANSWER:""",
    input_variables=["context", "question"]
)

SUMMARY_PROMPT = PromptTemplate(
    template="""You are TubeMind, an intelligent AI assistant. Analyze the following YouTube video transcript
and provide a comprehensive summary.

TRANSCRIPT:
{context}

Please provide:
1. **Summary** (2-3 paragraphs): A comprehensive summary of the video content
2. **Key Topics** (as a comma-separated list): The main topics discussed
3. **Key Points** (as a bulleted list): The most important takeaways

Format your response exactly as:
SUMMARY:
[your summary here]

TOPICS:
[topic1, topic2, topic3, ...]

KEY POINTS:
- [point 1]
- [point 2]
- [point 3]
...""",
    input_variables=["context"]
)


def _get_llm() -> ChatGoogleGenerativeAI:
    """Create a Gemini LLM instance."""
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
        convert_system_message_to_human=True,
    )


def _format_docs(docs) -> str:
    """Format retrieved documents into a context string."""
    formatted = []
    for doc in docs:
        timestamp = doc.metadata.get("timestamp", "")
        prefix = f"[{timestamp}] " if timestamp else ""
        formatted.append(f"{prefix}{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


def _extract_sources(docs) -> list:
    """Extract source information from retrieved documents."""
    sources = []
    for doc in docs:
        sources.append({
            "text": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            "timestamp": doc.metadata.get("timestamp", None),
        })
    return sources


async def ask_question(video_id: str, question: str) -> RAGResponse:
    """
    Ask a question about a video using the RAG pipeline.
    
    Args:
        video_id: The YouTube video ID
        question: The user's question
        
    Returns:
        RAGResponse with the answer and source chunks
    """
    logger.info(f"RAG query for video {video_id}: {question[:100]}...")

    # Get retriever for this video
    retriever = get_retriever(video_id)

    # Retrieve relevant documents
    retrieved_docs = retriever.invoke(question)

    if not retrieved_docs:
        return RAGResponse(
            answer="I couldn't find relevant information in this video's transcript to answer your question.",
            sources=[]
        )

    # Extract sources before formatting
    sources = _extract_sources(retrieved_docs)

    # Build the chain
    llm = _get_llm()
    context_text = _format_docs(retrieved_docs)

    # Create the prompt with context and question
    final_prompt = CHAT_PROMPT.invoke({
        "context": context_text,
        "question": question
    })

    # Generate answer
    response = llm.invoke(final_prompt)
    answer = response.content

    logger.info(f"RAG response generated: {len(answer)} chars, {len(sources)} sources")

    return RAGResponse(answer=answer, sources=sources)


async def generate_summary(video_id: str) -> dict:
    """
    Generate a comprehensive summary of a video.
    
    Args:
        video_id: The YouTube video ID
        
    Returns:
        Dict with 'summary', 'topics', and 'key_points'
    """
    logger.info(f"Generating summary for video: {video_id}")

    # Retrieve many chunks to cover the full video
    retriever = get_retriever(video_id, k=20)

    # Use a broad query to get diverse chunks
    docs = retriever.invoke("summarize the main topics and key points discussed in this video")
    context_text = _format_docs(docs)

    llm = _get_llm()
    final_prompt = SUMMARY_PROMPT.invoke({"context": context_text})
    response = llm.invoke(final_prompt)

    # Parse the structured response
    content = response.content
    result = _parse_summary_response(content)

    logger.info(f"Summary generated for video {video_id}")
    return result


def _parse_summary_response(content: str) -> dict:
    """Parse the structured summary response from the LLM."""
    summary = ""
    topics = []
    key_points = []

    sections = content.split("\n")
    current_section = None

    for line in sections:
        line_stripped = line.strip()
        if line_stripped.startswith("SUMMARY:"):
            current_section = "summary"
            continue
        elif line_stripped.startswith("TOPICS:"):
            current_section = "topics"
            continue
        elif line_stripped.startswith("KEY POINTS:"):
            current_section = "key_points"
            continue

        if current_section == "summary":
            summary += line + "\n"
        elif current_section == "topics" and line_stripped:
            topics = [t.strip() for t in line_stripped.split(",") if t.strip()]
        elif current_section == "key_points" and line_stripped.startswith("- "):
            key_points.append(line_stripped[2:])

    return {
        "summary": summary.strip() or content,
        "topics": topics or ["General"],
        "key_points": key_points or ["See summary above"],
    }
