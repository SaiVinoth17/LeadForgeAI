import { useEffect } from 'react';
import { useForgeStore } from '../store/useForgeStore';

const WS_URL = (import.meta as any).env?.VITE_WS_URL || 'ws://127.0.0.1:49281/ws/v5/stream';

export function useWebSocket(url: string = WS_URL) {
  const addTimelineEvent = useForgeStore((state) => state.addTimelineEvent);

  useEffect(() => {
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(url);

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.action && payload.detail) {
            addTimelineEvent({
              time: payload.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              action: payload.action,
              detail: payload.detail,
            });
          }
        } catch (e) {
          console.error("WebSocket message parse error", e);
        }
      };

      ws.onerror = (err) => {
        console.warn("WebSocket stream notice:", err);
      };
    } catch (e) {
      console.warn("WebSocket initialization error:", e);
    }

    return () => {
      if (ws) ws.close();
    };
  }, [url, addTimelineEvent]);
}
