"use client";
/**
 * useExecutionWebSocket - React Hook for Execution Streaming
 * ===========================================================
 * Provides real-time WebSocket connection for agent execution updates.
 *
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Heartbeat/ping-pong to detect stale connections
 * - Connection state management
 * - SSE fallback awareness (if WS fails, caller can switch to SSE)
 * - Visibility-aware: pauses reconnection when tab is hidden
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface UseExecutionWebSocketOptions {
  /** Full WebSocket URL, e.g. wss://backend.railway.app/api/v2/ws/execute/{id} */
  url: string;
  userId?: string;
  conversationId?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: (reason: string) => void;
  onError?: (error: Event) => void;
  /** Base reconnect interval in ms (will use exponential backoff) */
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  /** If false, the hook will not connect automatically */
  enabled?: boolean;
}

export interface UseExecutionWebSocketReturn {
  connected: boolean;
  connecting: boolean;
  error: Error | null;
  /** Number of reconnect attempts so far */
  reconnectAttempts: number;
  sendMessage: (message: WebSocketMessage) => void;
  disconnect: () => void;
  reconnect: () => void;
}

export function useExecutionWebSocket(
  options: UseExecutionWebSocketOptions
): UseExecutionWebSocketReturn {
  const {
    url,
    userId,
    conversationId,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectInterval = 2000,
    maxReconnectAttempts = 10,
    heartbeatInterval = 25000,
    enabled = true,
  } = options;

  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isManualDisconnectRef = useRef(false);
  const lastPongRef = useRef<number>(Date.now());

  // Stable refs for callbacks
  const onMessageRef = useRef(onMessage);
  const onConnectRef = useRef(onConnect);
  const onDisconnectRef = useRef(onDisconnect);
  const onErrorRef = useRef(onError);
  useEffect(() => { onMessageRef.current = onMessage; }, [onMessage]);
  useEffect(() => { onConnectRef.current = onConnect; }, [onConnect]);
  useEffect(() => { onDisconnectRef.current = onDisconnect; }, [onDisconnect]);
  useEffect(() => { onErrorRef.current = onError; }, [onError]);

  // Build WebSocket URL with query params
  const buildUrl = useCallback(() => {
    try {
      const wsUrl = new URL(url);
      if (userId) wsUrl.searchParams.set('user_id', userId);
      if (conversationId) wsUrl.searchParams.set('conversation_id', conversationId);
      return wsUrl.toString();
    } catch {
      return url;
    }
  }, [url, userId, conversationId]);

  // Clear timers
  const clearTimers = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
      heartbeatTimerRef.current = null;
    }
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  }, []);

  // Start heartbeat with stale connection detection
  const startHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
    }
    lastPongRef.current = Date.now();
    heartbeatTimerRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        // Check if we haven't received a pong in 2x heartbeat interval
        const timeSinceLastPong = Date.now() - lastPongRef.current;
        if (timeSinceLastPong > heartbeatInterval * 2.5) {
          console.warn('[WS] Stale connection detected, reconnecting...');
          wsRef.current?.close(4000, 'Stale connection');
          return;
        }
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!enabled) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    if (wsRef.current?.readyState === WebSocket.CONNECTING) return;

    setConnecting(true);
    setError(null);

    try {
      const wsUrl = buildUrl();
      console.log('[WS] Connecting to:', wsUrl);
      const ws = new WebSocket(wsUrl);

      // Connection timeout — if not open in 10s, close and retry
      const connectTimeout = setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN) {
          console.warn('[WS] Connection timeout, closing...');
          ws.close(4001, 'Connection timeout');
        }
      }, 10000);

      ws.onopen = () => {
        clearTimeout(connectTimeout);
        console.log('[WS] Connected');
        setConnected(true);
        setConnecting(false);
        setError(null);
        reconnectAttemptsRef.current = 0;
        setReconnectAttempts(0);
        isManualDisconnectRef.current = false;

        // Subscribe to conversation if provided
        if (conversationId) {
          ws.send(JSON.stringify({
            type: 'subscribe',
            channel: 'conversation',
            conversation_id: conversationId,
          }));
        }

        startHeartbeat();
        onConnectRef.current?.();
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          // Handle pong silently but update timestamp
          if (message.type === 'pong') {
            lastPongRef.current = Date.now();
            return;
          }
          if (message.type === 'connection.established') {
            lastPongRef.current = Date.now();
            console.log('[WS] Session ID:', message.session_id);
            return;
          }
          onMessageRef.current?.(message);
        } catch (err) {
          console.error('[WS] Failed to parse message:', err);
        }
      };

      ws.onclose = (event) => {
        clearTimeout(connectTimeout);
        console.log('[WS] Disconnected:', event.code, event.reason);
        setConnected(false);
        setConnecting(false);

        if (heartbeatTimerRef.current) {
          clearInterval(heartbeatTimerRef.current);
          heartbeatTimerRef.current = null;
        }

        const reason = event.wasClean ? 'Clean disconnect' : `Code: ${event.code}`;
        onDisconnectRef.current?.(reason);

        // Auto-reconnect with exponential backoff
        if (!isManualDisconnectRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          setReconnectAttempts(reconnectAttemptsRef.current);

          // Exponential backoff: 2s, 4s, 8s, 16s, 30s max
          const delay = Math.min(
            reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1),
            30000
          );
          console.log(`[WS] Reconnecting in ${delay}ms... Attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts}`);

          reconnectTimerRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError(new Error(`Failed to connect after ${maxReconnectAttempts} attempts`));
        }
      };

      ws.onerror = (event) => {
        clearTimeout(connectTimeout);
        console.error('[WS] Error:', event);
        setError(new Error('WebSocket connection error'));
        onErrorRef.current?.(event);
      };

      wsRef.current = ws;
    } catch (err) {
      setConnecting(false);
      setError(err instanceof Error ? err : new Error('Failed to connect'));
    }
  }, [buildUrl, conversationId, enabled, maxReconnectAttempts, reconnectInterval, startHeartbeat]);

  // Disconnect
  const disconnect = useCallback(() => {
    isManualDisconnectRef.current = true;
    clearTimers();
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }
    setConnected(false);
    setConnecting(false);
  }, [clearTimers]);

  // Reconnect (manual)
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setReconnectAttempts(0);
    isManualDisconnectRef.current = false;
    setTimeout(() => connect(), 100);
  }, [connect, disconnect]);

  // Send message
  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('[WS] Cannot send message, not connected');
    }
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    if (enabled) {
      connect();
    }
    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled]);

  // Visibility-aware: reconnect when tab becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && enabled && !connected && !connecting) {
        console.log('[WS] Tab visible, reconnecting...');
        reconnect();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [enabled, connected, connecting, reconnect]);

  return {
    connected,
    connecting,
    error,
    reconnectAttempts,
    sendMessage,
    disconnect,
    reconnect,
  };
}

export default useExecutionWebSocket;
