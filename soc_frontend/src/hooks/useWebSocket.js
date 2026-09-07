// useWebSocket.js — shared hook for WebSocket connections with auto-reconnect
import { useEffect, useRef, useState, useCallback } from 'react';

const WS_BASE = import.meta.env.VITE_WS_URL || '';

export function useWebSocket(path, onMessage) {
  const [status, setStatus] = useState('connecting'); // connecting | connected | disconnected
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    let url;
    if (WS_BASE) {
      const base = WS_BASE.replace(/\/$/, '');
      url = `${base}${path}`;
    } else {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      url = `${protocol}//${window.location.host}${path}`;
    }

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      setStatus('connecting');

      ws.onopen = () => setStatus('connected');

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          onMessageRef.current(data);
        } catch { /* ignore malformed frames */ }
      };

      ws.onerror = () => setStatus('disconnected');

      ws.onclose = () => {
        setStatus('disconnected');
        reconnectRef.current = setTimeout(connect, 3000);
      };
    } catch {
      setStatus('disconnected');
      reconnectRef.current = setTimeout(connect, 3000);
    }
  }, [path]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return status;
}
