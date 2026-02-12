"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";

interface LiveScreenProps {
  /** Base64 JPEG screenshot from the browser */
  screenshot: string | null;
  /** Current URL being browsed */
  url: string;
  /** Current page title */
  title: string;
  /** Whether the agent is actively browsing */
  isActive: boolean;
  /** Current action being performed */
  currentAction?: string;
  /** WebSocket URL for real-time updates (optional) */
  wsUrl?: string;
}

export default function LiveScreen({
  screenshot,
  url,
  title,
  isActive,
  currentAction,
  wsUrl,
}: LiveScreenProps) {
  const [wsScreenshot, setWsScreenshot] = useState<string | null>(null);
  const [wsUrl2, setWsUrl2] = useState<string>("");
  const [wsTitle, setWsTitle] = useState<string>("");
  const wsRef = useRef<WebSocket | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  // Use WebSocket screenshot if available, otherwise use prop
  const displayScreenshot = wsScreenshot || screenshot;
  const displayUrl = wsUrl2 || url;
  const displayTitle = wsTitle || title;

  // Connect to WebSocket for real-time screenshots
  useEffect(() => {
    if (!wsUrl) return;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "browser_screenshot") {
          setWsScreenshot(data.data.image);
          if (data.data.url) setWsUrl2(data.data.url);
          if (data.data.title) setWsTitle(data.data.title);
        }
      } catch (e) {
        // Ignore parse errors
      }
    };

    ws.onerror = () => {
      // WebSocket error — fall back to SSE screenshots
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [wsUrl]);

  return (
    <div className="flex flex-col h-full bg-[#1a1a2e] rounded-lg overflow-hidden border border-white/5">
      {/* Browser Chrome Bar */}
      <div className="flex items-center gap-2 px-3 py-2 bg-[#0d0d1a] border-b border-white/5">
        {/* Traffic lights */}
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
          <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
          <div className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
        </div>

        {/* URL Bar */}
        <div className="flex-1 flex items-center gap-2 bg-white/5 rounded-md px-3 py-1 text-xs">
          {isActive && (
            <div className="w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
          )}
          <span className="text-white/40 truncate font-mono">
            {displayUrl || "about:blank"}
          </span>
        </div>

        {/* Live badge */}
        {isActive && (
          <div className="flex items-center gap-1 px-2 py-0.5 bg-red-500/20 rounded text-[10px] text-red-400 font-medium">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
            LIVE
          </div>
        )}
      </div>

      {/* Screenshot Viewport */}
      <div className="flex-1 relative bg-[#0a0a1a] overflow-hidden">
        {displayScreenshot ? (
          <>
            <img
              ref={imgRef}
              src={`data:image/jpeg;base64,${displayScreenshot}`}
              alt={displayTitle || "Browser screenshot"}
              className="w-full h-full object-contain"
              style={{ imageRendering: "auto" }}
            />

            {/* Action overlay */}
            {isActive && currentAction && (
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  <span className="text-xs text-white/80 font-mono">
                    {currentAction}
                  </span>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-white/20 gap-3">
            <svg
              className="w-12 h-12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            <div className="text-center">
              <p className="text-sm font-medium text-white/30">
                {isActive
                  ? "Waiting for browser to load..."
                  : "Browser view will appear here"}
              </p>
              <p className="text-xs text-white/15 mt-1">
                {isActive
                  ? "Screenshots streaming in real-time"
                  : "Start an agent task to see live browsing"}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Status Bar */}
      {displayScreenshot && (
        <div className="flex items-center justify-between px-3 py-1.5 bg-[#0d0d1a] border-t border-white/5 text-[10px] text-white/30">
          <span className="truncate max-w-[60%]">
            {displayTitle || "Untitled"}
          </span>
          <span>
            {isActive ? "Browsing..." : "Screenshot captured"}
          </span>
        </div>
      )}
    </div>
  );
}
