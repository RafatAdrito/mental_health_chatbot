import { useEffect, useRef, useCallback } from "react";
import { BASE_URL, getToken } from "../api/client";
import { sendMessageRest } from "../api/chat";
import useStore from "../store";

export function useWebSocket() {
  const ws = useRef(null);
  const connectTimer = useRef(null);
  const sessionId = useStore((s) => s.sessionId);

  useEffect(() => {
    const store = useStore.getState();

    const disposeSocket = (socket) => {
      if (!socket) return;
      if (socket.readyState === WebSocket.CONNECTING) {
        socket.onopen = () => socket.close();
        socket.onmessage = null;
        socket.onerror = null;
        socket.onclose = null;
        return;
      }
      socket.onopen = null;
      socket.onmessage = null;
      socket.onerror = null;
      socket.onclose = null;
      if (socket.readyState === WebSocket.OPEN) socket.close();
    };

    if (connectTimer.current) {
      clearTimeout(connectTimer.current);
      connectTimer.current = null;
    }

    if (!sessionId) {
      if (ws.current) {
        const socket = ws.current;
        ws.current = null;
        disposeSocket(socket);
      }
      store.setIsConnected(false);
      return;
    }

    // Delay socket creation so StrictMode's throwaway mount can clean up first in dev.
    connectTimer.current = setTimeout(() => {
      const token = getToken();
      const wsBase = BASE_URL.replace(/^http/, "ws");
      const url = `${wsBase}/api/v1/chat/ws/${sessionId}${token ? `?token=${encodeURIComponent(token)}` : ""}`;
      const socket = new WebSocket(url);
      ws.current = socket;
      connectTimer.current = null;

      socket.onopen = () => {
        if (ws.current !== socket) return;
        useStore.getState().setIsConnected(true);
      };

      socket.onmessage = (event) => {
        if (ws.current !== socket) return;
        const msg = JSON.parse(event.data);
        const activeStore = useStore.getState();
        switch (msg.type) {
          case "token":
            activeStore.appendStreamingToken(msg.data);
            activeStore.setIsStreaming(true);
            break;
          case "crisis_alert":
            activeStore.setShowCrisisAlert(true);
            break;
          case "done":
            activeStore.finalizeStreamingMessage();
            break;
          case "error":
            activeStore.clearStreamingContent();
            activeStore.addMessage({
              role: "assistant",
              content: msg.data || "Something went wrong. Please try again.",
            });
            activeStore.setIsStreaming(false);
            activeStore.setIsSending(false);
            break;
          default:
            break;
        }
      };

      socket.onerror = () => {
        if (ws.current !== socket) return;
        const activeStore = useStore.getState();
        activeStore.setIsConnected(false);
        activeStore.clearStreamingContent();
        activeStore.setIsStreaming(false);
        activeStore.setIsSending(false);
      };

      socket.onclose = () => {
        if (ws.current !== socket) return;
        ws.current = null;
        useStore.getState().setIsConnected(false);
      };
    }, 0);

    return () => {
      if (connectTimer.current) {
        clearTimeout(connectTimer.current);
        connectTimer.current = null;
      }
      if (ws.current) {
        const socket = ws.current;
        ws.current = null;
        disposeSocket(socket);
      }
      useStore.getState().setIsConnected(false);
    };
  }, [sessionId]);

  const sendMessage = useCallback((text) => {
    const store = useStore.getState();
    const { userLocation, sessionId: currentSessionId } = store;
    const payload = { message: text };
    if (userLocation) {
      payload.latitude = userLocation.latitude;
      payload.longitude = userLocation.longitude;
    }

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(payload));
      return;
    }

    if (!currentSessionId) {
      store.setIsSending(false);
      return;
    }

    sendMessageRest({
      sessionId: currentSessionId,
      message: text,
      latitude: userLocation?.latitude ?? null,
      longitude: userLocation?.longitude ?? null,
    })
      .then((res) => {
        store.addMessage({ role: "assistant", content: res.response });
        if (res.risk_level === "high" || res.risk_level === "critical") {
          store.setShowCrisisAlert(true);
        }
      })
      .catch(() => {
        store.addMessage({
          role: "assistant",
          content:
            "Unable to reach the server. Please check your connection and try again.",
        });
      })
      .finally(() => {
        store.setIsSending(false);
        store.setIsStreaming(false);
      });
  }, []);

  return { sendMessage };
}
