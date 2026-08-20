import { useEffect, useRef, useState } from "react";
import { checkModalStatus } from "../api";

type Status = "idle" | "starting" | "live" | "error";

const POLL_INTERVAL_MS = 5000;
const MAX_POLLS = 60; // ~5 minutes of polling before giving up

export default function ModalStatusBadge() {
  const [status, setStatus] = useState<Status>("idle");
  const [detail, setDetail] = useState<string | null>(null);
  const pollCount = useRef(0);
  const intervalRef = useRef<number | null>(null);

  function stopPolling() {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }

  useEffect(() => stopPolling, []);

  async function checkOnce() {
    try {
      const result = await checkModalStatus();
      setDetail(result.detail ?? null);
      if (result.status === "live") {
        setStatus("live");
        stopPolling();
      } else if (result.status === "error") {
        setStatus("error");
      } else {
        setStatus("starting");
      }
    } catch (err) {
      setStatus("error");
      setDetail(err instanceof Error ? err.message : String(err));
    }
  }

  function handleWarmUp() {
    stopPolling();
    pollCount.current = 0;
    setStatus("starting");
    setDetail(null);
    checkOnce();
    intervalRef.current = window.setInterval(() => {
      pollCount.current += 1;
      if (pollCount.current >= MAX_POLLS) {
        stopPolling();
        setStatus((current) => (current === "live" ? current : "error"));
        setDetail("Timed out waiting for the model — check the Modal dashboard directly.");
        return;
      }
      checkOnce();
    }, POLL_INTERVAL_MS);
  }

  const label =
    status === "idle"
      ? "Model: Unknown"
      : status === "starting"
        ? "Model: Starting…"
        : status === "live"
          ? "Model: Live"
          : "Model: Check Failed";

  return (
    <div className="modal-status">
      <span className={`modal-status-dot status-${status}`} aria-hidden="true" />
      <span className="modal-status-label">{label}</span>
      <button
        className="modal-status-button"
        onClick={handleWarmUp}
        disabled={status === "starting"}
      >
        {status === "idle" ? "Warm Up" : "Recheck"}
      </button>
      {detail && status === "error" && <span className="modal-status-detail">{detail}</span>}
    </div>
  );
}
