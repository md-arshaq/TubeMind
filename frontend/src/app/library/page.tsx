"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { listVideos, deleteVideo, type Video } from "@/lib/api";

export default function LibraryPage() {
  const router = useRouter();
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadVideos();
  }, []);

  async function loadVideos() {
    try {
      const data = await listVideos();
      setVideos(data.videos);
    } catch (err: any) {
      setError(err.message || "Failed to load videos.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(videoId: string) {
    if (!confirm("Delete this video and all its chat history?")) return;
    setDeletingId(videoId);
    try {
      await deleteVideo(videoId);
      setVideos((prev) => prev.filter((v) => v.video_id !== videoId));
    } catch (err: any) {
      setError(err.message || "Failed to delete video.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="relative min-h-screen">
      {/* Background Orbs */}
      <div className="orb orb-1 opacity-20" />
      <div className="orb orb-2 opacity-20" />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 md:px-12 border-b border-(--border-color)">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-linear-to-br from-[#8b5cf6] to-[#06b6d4] flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
          </div>
          <span className="text-xl font-bold tracking-tight">
            Tube<span className="gradient-text">Mind</span>
          </span>
        </Link>
        <Link href="/" className="btn-primary text-sm py-2 px-4">
          + Analyze New Video
        </Link>
      </nav>

      {/* Content */}
      <main className="relative z-10 max-w-6xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <img src="/library_logo.png" alt="Library" className="w-8 h-8" />
            My Video Library
          </h1>
          <p className="text-(--text-secondary)">
            {videos.length} video{videos.length !== 1 ? "s" : ""} analyzed
          </p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-xl bg-[rgba(244,63,94,0.1)] border border-[rgba(244,63,94,0.2)] text-[#fb7185] text-sm">
            {error}
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="glass-card overflow-hidden">
                <div className="skeleton aspect-video" />
                <div className="p-4 space-y-3">
                  <div className="skeleton h-5 w-3/4" />
                  <div className="skeleton h-4 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        ) : videos.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-20 h-20 rounded-2xl bg-linear-to-br from-[rgba(139,92,246,0.1)] to-[rgba(6,182,212,0.1)] flex items-center justify-center mb-6">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="1.5">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                <line x1="8" y1="21" x2="16" y2="21" />
                <line x1="12" y1="17" x2="12" y2="21" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">No videos yet</h3>
            <p className="text-(--text-muted) mb-6 max-w-sm">
              Start by analyzing your first YouTube video. Paste a URL on the home page to get started.
            </p>
            <Link href="/" className="btn-primary">
              Analyze Your First Video
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 stagger">
            {videos.map((video) => (
              <div
                key={video.video_id}
                className="glass-card overflow-hidden group cursor-pointer"
                onClick={() => router.push(`/chat/${video.video_id}`)}
              >
                {/* Thumbnail */}
                <div className="relative aspect-video bg-(--bg-tertiary) overflow-hidden">
                  {video.thumbnail ? (
                    <img
                      src={video.thumbnail}
                      alt={video.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-(--text-muted)">
                      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <polygon points="5 3 19 12 5 21 5 3" />
                      </svg>
                    </div>
                  )}
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-linear-to-t from-[rgba(0,0,0,0.7)] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-3">
                    <span className="text-xs text-white font-medium flex items-center gap-1">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                      </svg>
                      Chat with this video
                    </span>
                  </div>
                  {/* Status Badge */}
                  <div className="absolute top-2 right-2">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${video.status === "ready"
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : video.status === "processing"
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                          : "bg-red-500/20 text-red-400 border border-red-500/30"
                      }`}>
                      {video.status}
                    </span>
                  </div>
                </div>

                {/* Info */}
                <div className="p-4">
                  <h3 className="font-semibold text-sm mb-1 line-clamp-2">
                    {video.title}
                  </h3>
                  <div className="flex items-center justify-between mt-3">
                    <span className="text-xs text-(--text-muted)">
                      {video.chunks_count} chunks • {new Date(video.created_at).toLocaleDateString()}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(video.video_id);
                      }}
                      disabled={deletingId === video.video_id}
                      className="text-(--text-muted) hover:text-[#fb7185] transition-colors p-1"
                      title="Delete video"
                    >
                      {deletingId === video.video_id ? (
                        <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="60" strokeLinecap="round" className="opacity-30" />
                          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="15 45" strokeLinecap="round" />
                        </svg>
                      ) : (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                      )}
                    </button>
                  </div>
                  {/* Topics */}
                  {video.topics && video.topics.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {video.topics.slice(0, 3).map((topic, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-[rgba(139,92,246,0.1)] text-[#a78bfa]"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
