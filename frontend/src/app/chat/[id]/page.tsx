"use client";

import { useState, useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  getVideo,
  askQuestion,
  getChatHistory,
  generateSummary,
  type Video,
  type ChatMessage,
  type SummaryResult,
} from "@/lib/api";

export default function ChatPage() {
  const params = useParams();
  const videoId = params.id as string;

  const [video, setVideo] = useState<Video | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState<SummaryResult | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [showSources, setShowSources] = useState<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load video and chat history
  useEffect(() => {
    async function loadData() {
      try {
        const [videoData, historyData] = await Promise.all([
          getVideo(videoId),
          getChatHistory(videoId),
        ]);
        setVideo(videoData);
        setMessages(historyData.messages);

        if (videoData.summary) {
          setSummary({
            video_id: videoData.video_id,
            summary: videoData.summary,
            topics: videoData.topics || [],
            key_points: [],
          });
        }
      } catch (err: any) {
        setError(err.message || "Failed to load video data.");
      } finally {
        setPageLoading(false);
      }
    }
    loadData();
  }, [videoId]);

  // Auto-scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const q = question.trim();
    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const response = await askQuestion(videoId, q);
      setMessages((prev) => [...prev, response]);
    } catch (err: any) {
      setError(err.message || "Failed to get answer.");
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSummary = async () => {
    if (summaryLoading) return;
    setSummaryLoading(true);
    try {
      const result = await generateSummary(videoId);
      setSummary(result);
    } catch (err: any) {
      setError(err.message || "Failed to generate summary.");
    } finally {
      setSummaryLoading(false);
    }
  };

  if (pageLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <svg className="animate-spin w-10 h-10 text-(--brand-primary)" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="60" strokeLinecap="round" className="opacity-20" />
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="15 45" strokeLinecap="round" />
          </svg>
          <p className="text-(--text-muted)">Loading video...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-4 md:px-6 py-3 border-b border-(--border-color) bg-(--bg-secondary)">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-linear-to-br from-[#8b5cf6] to-[#06b6d4] flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
            </div>
            <span className="text-lg font-bold tracking-tight hidden sm:block">
              Tube<span className="gradient-text">Mind</span>
            </span>
          </Link>
          <span className="text-(--text-muted) hidden md:block">|</span>
          <h1 className="text-sm font-medium text-(--text-secondary) truncate max-w-xs md:max-w-md">
            {video?.title || `Video ${videoId}`}
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/library" className="btn-ghost text-xs py-1.5 px-3 flex items-center gap-1.5">
            <img src="/library_logo.png" alt="Library" className="w-4 h-4" />
            Library
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left Panel: Video + Summary */}
        <div className="lg:w-[420px] xl:w-[480px] border-r border-(--border-color) bg-(--bg-secondary) overflow-y-auto">
          {/* YouTube Embed */}
          <div className="aspect-video bg-black">
            <iframe
              src={`https://www.youtube.com/embed/${videoId}`}
              className="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title="YouTube Video Player"
            />
          </div>

          {/* Video Info */}
          <div className="p-4 space-y-4">
            <div>
              <h2 className="text-base font-semibold">{video?.title}</h2>
              {video?.channel && (
                <p className="text-sm text-(--text-muted) mt-1">{video.channel}</p>
              )}
              <div className="flex items-center gap-3 mt-2 text-xs text-(--text-muted)">
                <span className="flex items-center gap-1">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <line x1="3" y1="9" x2="21" y2="9" />
                  </svg>
                  {video?.chunks_count} chunks indexed
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  {video?.status}
                </span>
              </div>
            </div>

            {/* Topics */}
            {summary?.topics && summary.topics.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {summary.topics.map((topic, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 rounded-full text-xs font-medium bg-[rgba(139,92,246,0.1)] text-[#a78bfa] border border-[rgba(139,92,246,0.15)]"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            )}

            {/* Summary Section */}
            <div className="glass-card p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--brand-primary)" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                  Summary
                </h3>
                <button
                  onClick={handleSummary}
                  disabled={summaryLoading}
                  className="text-xs text-(--brand-primary) hover:underline disabled:opacity-50"
                >
                  {summaryLoading ? "Generating..." : summary ? "Regenerate" : "Generate"}
                </button>
              </div>
              {summaryLoading ? (
                <div className="space-y-2">
                  <div className="skeleton h-4 w-full" />
                  <div className="skeleton h-4 w-5/6" />
                  <div className="skeleton h-4 w-4/6" />
                </div>
              ) : summary ? (
                <div className="text-sm text-(--text-secondary) leading-relaxed">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({node, ...props}) => <p className="mb-4 last:mb-0" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-4 space-y-2 marker:text-(--brand-primary)" {...props} />,
                      ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-4 space-y-2 marker:text-(--brand-primary)" {...props} />,
                      li: ({node, ...props}) => <li className="pl-1" {...props} />,
                      strong: ({node, ...props}) => <strong className="font-semibold text-(--text-primary)" {...props} />,
                      h3: ({node, ...props}) => <h3 className="text-base font-semibold mt-6 mb-3 text-(--text-primary)" {...props} />
                    }}
                  >
                    {summary.summary}
                  </ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm text-(--text-muted) italic">
                  Click &ldquo;Generate&rdquo; to create an AI summary of this video.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel: Chat */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
            {messages.length === 0 && !loading && (
              <div className="flex flex-col items-center justify-center h-full text-center gap-4 py-12">
                <div className="w-16 h-16 rounded-2xl bg-linear-to-br from-[rgba(139,92,246,0.15)] to-[rgba(6,182,212,0.1)] flex items-center justify-center">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--brand-primary)" strokeWidth="1.5">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-1">Start a Conversation</h3>
                  <p className="text-sm text-(--text-muted) max-w-sm">
                    Ask anything about this video. I&apos;ll find the relevant parts and give you a detailed answer.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 max-w-md">
                  {[
                    "What are the main topics discussed?",
                    "Can you summarize the key points?",
                    "What conclusions were drawn?",
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => {
                        setQuestion(suggestion);
                        inputRef.current?.focus();
                      }}
                      className="px-3 py-1.5 rounded-full text-xs border border-(--border-color) text-(--text-secondary) hover:border-(--brand-primary) hover:text-(--text-primary) transition-all duration-200"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className="fade-in space-y-4">
                {/* User Question */}
                <div className="flex justify-end">
                  <div className="max-w-[80%] lg:max-w-[70%] px-4 py-3 rounded-2xl rounded-br-md bg-linear-to-r from-[#8b5cf6] to-[#7c3aed] text-white">
                    <p className="text-sm">{msg.question}</p>
                  </div>
                </div>
                {/* AI Answer */}
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-lg bg-linear-to-br from-[rgba(6,182,212,0.2)] to-[rgba(139,92,246,0.2)] flex items-center justify-center shrink-0 mt-1">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--brand-secondary)" strokeWidth="2">
                      <path d="M12 2L2 7l10 5 10-5-10-5z" />
                      <path d="M2 17l10 5 10-5" />
                      <path d="M2 12l10 5 10-5" />
                    </svg>
                  </div>
                  <div className="max-w-[85%] lg:max-w-[75%]">
                    <div className="px-5 py-4 rounded-2xl rounded-tl-md bg-(--bg-tertiary) border border-(--border-color)">
                      <div className="text-sm text-(--text-primary) leading-relaxed">
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p: ({node, ...props}) => <p className="mb-4 last:mb-0" {...props} />,
                            ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-4 space-y-3 marker:text-(--brand-primary)" {...props} />,
                            ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-4 space-y-3 marker:text-(--brand-primary)" {...props} />,
                            li: ({node, ...props}) => <li className="pl-1" {...props} />,
                            strong: ({node, ...props}) => <strong className="font-semibold text-white" {...props} />,
                            h3: ({node, ...props}) => <h3 className="text-base font-semibold mt-6 mb-3 text-white" {...props} />
                          }}
                        >
                          {msg.answer}
                        </ReactMarkdown>
                      </div>
                    </div>
                    {/* Sources */}
                    {msg.sources.length > 0 && (
                      <div className="mt-2">
                        <button
                          onClick={() => setShowSources(showSources === msg.id ? null : msg.id)}
                          className="text-xs text-(--text-muted) hover:text-(--brand-primary) flex items-center gap-1 transition-colors"
                        >
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                            <polyline points="14 2 14 8 20 8" />
                          </svg>
                          {msg.sources.length} source{msg.sources.length > 1 ? "s" : ""}
                          <svg
                            width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                            className={`transition-transform ${showSources === msg.id ? "rotate-180" : ""}`}
                          >
                            <polyline points="6 9 12 15 18 9" />
                          </svg>
                        </button>
                        {showSources === msg.id && (
                          <div className="mt-2 space-y-2">
                            {msg.sources.map((source, i) => (
                              <div
                                key={i}
                                className="p-3 rounded-lg bg-[rgba(255,255,255,0.02)] border border-(--border-color) text-xs"
                              >
                                {source.timestamp && (
                                  <span className="inline-block px-1.5 py-0.5 rounded bg-[rgba(139,92,246,0.15)] text-[#a78bfa] font-mono text-[10px] mr-2 mb-1">
                                    ⏱ {source.timestamp}
                                  </span>
                                )}
                                <p className="text-(--text-muted) leading-relaxed">
                                  {source.text}
                                </p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {loading && (
              <div className="flex gap-3 fade-in">
                <div className="w-8 h-8 rounded-lg bg-linear-to-br from-[rgba(6,182,212,0.2)] to-[rgba(139,92,246,0.2)] flex items-center justify-center shrink-0 mt-1">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--brand-secondary)" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z" />
                    <path d="M2 17l10 5 10-5" />
                    <path d="M2 12l10 5 10-5" />
                  </svg>
                </div>
                <div className="px-4 py-3 rounded-2xl rounded-tl-md bg-(--bg-tertiary) border border-(--border-color)">
                  <div className="flex items-center gap-1.5">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="p-3 rounded-xl bg-[rgba(244,63,94,0.1)] border border-[rgba(244,63,94,0.2)] text-[#fb7185] text-sm">
                {error}
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Chat Input */}
          <form
            onSubmit={handleAsk}
            className="p-4 border-t border-(--border-color) bg-(--bg-secondary)"
          >
            <div className="flex items-center gap-3 max-w-4xl mx-auto">
              <input
                ref={inputRef}
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about this video..."
                className="input-glass flex-1"
                disabled={loading}
                id="chat-input"
              />
              <button
                type="submit"
                disabled={loading || !question.trim()}
                className="btn-primary px-5 py-3"
                id="send-button"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
