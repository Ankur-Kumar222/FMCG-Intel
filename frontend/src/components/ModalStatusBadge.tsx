import { useEffect, useRef, useState } from "react";
import { checkModalStatus } from "../api";

export type ModalStatus = "idle" | "starting" | "live" | "error";

const POLL_INTERVAL_MS = 5000;
const MAX_POLLS = 60; // ~5 minutes of polling before giving up

interface Props {
  onStatusChange: (status: ModalStatus) => void;
}

export default function ModalStatusBadge({ onStatusChange }: Props) {
  const [status, setStatus] = useState<ModalStatus>("idle");
  const [detail, setDetail] = useState<string | null>(null);
  const pollCount = useRef(0);
  const intervalRef = useRef<number | null>(null);

  function updateStatus(next: ModalStatus) {
    setStatus(next);
    onStatusChange(next);
  }

  function stopPolling() {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }

  async function checkOnce() {
    try {
      const result = await checkModalStatus();
      setDetail(result.detail ?? null);
      if (result.status === "live") {
        updateStatus("live");
        stopPolling();
      } else if (result.status === "error") {
        updateStatus("error");
      } else {
        updateStatus("starting");
      }
    } catch (err) {
      updateStatus("error");
      setDetail(err instanceof Error ? err.message : String(err));
    }
  }

  function startPolling() {
    stopPolling();
    pollCount.current = 0;
    updateStatus("starting");
    setDetail(null);
    checkOnce();
    intervalRef.current = window.setInterval(() => {
      pollCount.current += 1;
      if (pollCount.current >= MAX_POLLS) {
        stopPolling();
        setStatus((current) => {
          const next = current === "live" ? current : "error";
          onStatusChange(next);
          return next;
        });
        setDetail("Timed out waiting for the model — check the Modal dashboard directly.");
        return;
      }
      checkOnce();
    }, POLL_INTERVAL_MS);
  }

  useEffect(() => stopPolling, []);

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
        onClick={startPolling}
        disabled={status === "starting"}
      >
        {status === "idle" ? "Warm Up" : "Recheck"}
      </button>
      {detail && status === "error" && <span className="modal-status-detail">{detail}</span>}
    </div>
  );
}
