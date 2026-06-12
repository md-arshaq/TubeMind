"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeVideo } from "@/lib/api";
import Link from "next/link";

export default function Home() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError("");

    try {
      const video = await analyzeVideo(url.trim());
      router.push(`/chat/${video.video_id}`);
    } catch (err: any) {
      setError(err.message || "Failed to analyze video. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Animated Background Orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 md:px-12">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-linear-to-br from-[#8b5cf6] to-[#06b6d4] flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
          </div>
          <span className="text-xl font-bold tracking-tight">
            Tube<span className="gradient-text">Mind</span>
          </span>
        </div>
          <Link href="/library" className="btn-ghost flex items-center gap-2">
            <img src="/library_logo.png" alt="Library" className="w-5 h-5" /> My Library
          </Link>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center px-6 pt-16 md:pt-28 pb-20">
        {/* Badge */}
        <div className="fade-in mb-6">
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium bg-[rgba(139,92,246,0.12)] text-[#a78bfa] border border-[rgba(139,92,246,0.2)]">
            <span className="w-2 h-2 rounded-full bg-[#8b5cf6] pulse-ring" />
            Powered by Google Gemini AI
          </span>
        </div>

        {/* Headline */}
        <h1 className="fade-in-up text-center text-4xl md:text-6xl lg:text-7xl font-extrabold leading-[1.1] tracking-tight max-w-4xl mb-6">
          Chat with Any{" "}
          <span className="gradient-text">YouTube</span>{" "}
          Video
        </h1>

        {/* Subheadline */}
        <p className="fade-in-up text-center text-lg md:text-xl text-(--text-secondary) max-w-2xl mb-12" style={{ animationDelay: "0.15s" }}>
          Paste a YouTube link, and instantly get AI-powered summaries,
          ask questions, and explore video content like never before.
        </p>

        {/* URL Input */}
        <form
          onSubmit={handleSubmit}
          className="fade-in-up w-full max-w-2xl"
          style={{ animationDelay: "0.3s" }}
        >
          <div className="relative flex items-center gap-3 p-2 rounded-2xl bg-[rgba(255,255,255,0.04)] border border-(--border-color) focus-within:border-(--brand-primary) focus-within:shadow-[0_0_0_3px_rgba(139,92,246,0.15)] transition-all duration-300">
            {/* YouTube Icon */}
            <div className="pl-4 text-(--text-muted)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19.1c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.43z" fill="#FF0000" opacity="0.8"/>
                <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02" fill="white"/>
              </svg>
            </div>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste a YouTube URL here..."
              className="flex-1 bg-transparent text-(--text-primary) placeholder:text-(--text-muted) text-base outline-none py-3"
              disabled={loading}
              id="youtube-url-input"
            />
            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="btn-primary flex items-center gap-2 whitespace-nowrap"
              id="analyze-button"
            >
              {loading ? (
                <>
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="60" strokeLinecap="round" className="opacity-30" />
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="15 45" strokeLinecap="round" />
                  </svg>
                  Analyzing...
                </>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.3-4.3" />
                  </svg>
                  Analyze
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 rounded-xl bg-[rgba(244,63,94,0.1)] border border-[rgba(244,63,94,0.2)] text-[#fb7185] text-sm flex items-start gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mt-0.5 shrink-0">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {error}
            </div>
          )}
        </form>

        {/* Features */}
        <div className="stagger grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 max-w-4xl w-full">
          <FeatureCard
            icon={
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            }
            title="Chat with Videos"
            description="Ask any question about the video content and get AI-powered answers with timestamp references."
          />
          <FeatureCard
            icon={
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
            }
            title="Instant Summaries"
            description="Get comprehensive video summaries with key topics and takeaways in seconds."
          />
          <FeatureCard
            icon={
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                <line x1="8" y1="21" x2="16" y2="21" />
                <line x1="12" y1="17" x2="12" y2="21" />
              </svg>
            }
            title="Video Library"
            description="Build your personal library of analyzed videos. Return anytime to continue exploring."
          />
        </div>

        {/* Tech Stack Badge */}
        <div className="fade-in mt-16 flex flex-wrap items-center justify-center gap-3 text-xs text-(--text-muted)">
          <span>Built with</span>
          {["Next.js", "FastAPI", "LangChain", "Gemini AI", "ChromaDB"].map(
            (tech) => (
              <span
                key={tech}
                className="px-3 py-1 rounded-full border border-(--border-color) bg-[rgba(255,255,255,0.02)]"
              >
                {tech}
              </span>
            )
          )}
        </div>
      </main>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="glass-card p-6 flex flex-col gap-4">
      <div className="w-12 h-12 rounded-xl bg-linear-to-br from-[rgba(139,92,246,0.15)] to-[rgba(6,182,212,0.1)] flex items-center justify-center text-(--brand-primary)">
        {icon}
      </div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-sm text-(--text-secondary) leading-relaxed">
        {description}
      </p>
    </div>
  );
}
