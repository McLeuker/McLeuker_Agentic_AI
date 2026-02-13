"use client";
/**
 * useExecutionWebSocket - React Hook for Execution Streaming
 * ===========================================================
 * Provides real-time WebSocket connection for V4 agent execution updates.
 *
 * Features:
 * - Automatic reconnection
 * - Message handling
 * - State management
 * - Error handling
 * - Heartbeat/ping-pong
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface UseExecutionWebSocketOptions {
  /** Full WebSocket URL, e.g. wss://backend.railway.app/api/v4/ws/execute/{id} */
  url: string;
  userId?: string;
  conversationId?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: (reason: string) => void;
  onError?: (error: Event) => void;
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
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
    enabled = true,
  } = options;

  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isManualDisconnectRef = useRef(false);

  // Stable refs for callbacks to avoid re-renders
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
      // If URL parsing fails, return as-is
      return url;
    }
  }, [url, userId, conversationId]);

  // Clear heartbeat timer
  const clearHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
      heartbeatTimerRef.current = null;
    }
  }, []);

  // Start heartbeat
  const startHeartbeat = useCallback(() => {
    clearHeartbeat();
    heartbeatTimerRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, heartbeatInterval);
  }, [clearHeartbeat, heartbeatInterval]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!enabled) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnecting(true);
    setError(null);

    try {
      const wsUrl = buildUrl();
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('[V4 WebSocket] Connected');
        setConnected(true);
        setConnecting(false);
        setError(null);
        reconnectAttemptsRef.current = 0;
        isManualDisconnectRef.current = false;

        // Subscribe to conversation
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
          // Silently handle pong
          if (message.type === 'pong') return;
          if (message.type === 'connection.established') {
            console.log('[V4 WebSocket] Session ID:', message.session_id);
            return;
          }
          onMessageRef.current?.(message);
        } catch (err) {
          console.error('[V4 WebSocket] Failed to parse message:', err);
        }
      };

      ws.onclose = (event) => {
        console.log('[V4 WebSocket] Disconnected:', event.code, event.reason);
        setConnected(false);
        setConnecting(false);
        clearHeartbeat();

        const reason = event.wasClean ? 'Clean disconnect' : `Code: ${event.code}`;
        onDisconnectRef.current?.(reason);

        // Auto-reconnect
        if (!isManualDisconnectRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`[V4 WebSocket] Reconnecting... Attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts}`);
          reconnectTimerRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (event) => {
        console.error('[V4 WebSocket] Error:', event);
        setError(new Error('WebSocket connection error'));
        onErrorRef.current?.(event);
      };

      wsRef.current = ws;
    } catch (err) {
      setConnecting(false);
      setError(err instanceof Error ? err : new Error('Failed to connect'));
    }
  }, [buildUrl, conversationId, enabled, maxReconnectAttempts, reconnectInterval, startHeartbeat, clearHeartbeat]);

  // Disconnect
  const disconnect = useCallback(() => {
    isManualDisconnectRef.current = true;
    clearHeartbeat();
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }
    setConnected(false);
    setConnecting(false);
  }, [clearHeartbeat]);

  // Reconnect
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    isManualDisconnectRef.current = false;
    setTimeout(() => connect(), 100);
  }, [connect, disconnect]);

  // Send message
  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('[V4 WebSocket] Cannot send message, not connected');
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

  return {
    connected,
    connecting,
    error,
    sendMessage,
    disconnect,
    reconnect,
  };
}

export default useExecutionWebSocket;
