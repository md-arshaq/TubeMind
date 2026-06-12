/**
 * TubeMind API Client
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Types ───────────────────────────────────────────

export interface Video {
  id: string;
  video_id: string;
  title: string;
  channel: string | null;
  thumbnail: string | null;
  duration: string | null;
  chunks_count: number;
  status: "processing" | "ready" | "failed";
  summary: string | null;
  topics: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface SourceChunk {
  text: string;
  timestamp: string | null;
  relevance_score: number | null;
}

export interface ChatMessage {
  id: string;
  question: string;
  answer: string;
  sources: SourceChunk[];
  created_at: string;
}

export interface SummaryResult {
  video_id: string;
  summary: string;
  topics: string[];
  key_points: string[];
}

// ─── API Functions ───────────────────────────────────

async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

/** Submit a YouTube URL for analysis */
export async function analyzeVideo(url: string): Promise<Video> {
  return apiFetch<Video>("/api/videos", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

/** List all analyzed videos */
export async function listVideos(): Promise<{ videos: Video[]; total: number }> {
  return apiFetch("/api/videos");
}

/** Get a specific video by ID */
export async function getVideo(videoId: string): Promise<Video> {
  return apiFetch<Video>(`/api/videos/${videoId}`);
}

/** Delete a video */
export async function deleteVideo(videoId: string): Promise<void> {
  return apiFetch(`/api/videos/${videoId}`, { method: "DELETE" });
}

/** Ask a question about a video */
export async function askQuestion(
  videoId: string,
  question: string
): Promise<ChatMessage> {
  return apiFetch<ChatMessage>(`/api/videos/${videoId}/chat`, {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

/** Get chat history for a video */
export async function getChatHistory(
  videoId: string
): Promise<{ messages: ChatMessage[]; total: number }> {
  return apiFetch(`/api/videos/${videoId}/chat/history`);
}

/** Generate a summary for a video */
export async function generateSummary(
  videoId: string
): Promise<SummaryResult> {
  return apiFetch<SummaryResult>(`/api/videos/${videoId}/summary`, {
    method: "POST",
  });
}

/** Health check */
export async function healthCheck(): Promise<{
  status: string;
  version: string;
}> {
  return apiFetch("/health");
}
