import { useEffect, useState } from "react";
import { NewsletterRun, fetchLatest, generateNewsletter } from "./api";
import RunButton from "./components/RunButton";
import NewsletterView from "./components/NewsletterView";
import DownloadButtons from "./components/DownloadButtons";
import ModalStatusBadge from "./components/ModalStatusBadge";

const EDITION_DATE_FORMAT: Intl.DateTimeFormatOptions = {
  weekday: "long",
  year: "numeric",
  month: "long",
  day: "numeric",
};

export default function App() {
  const [run, setRun] = useState<NewsletterRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialLoad, setInitialLoad] = useState(true);

  useEffect(() => {
    fetchLatest()
      .then(setRun)
      .catch(() => setRun(null))
      .finally(() => setInitialLoad(false));
  }, []);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const newRun = await generateNewsletter();
      setRun(newRun);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  const today = new Date().toLocaleDateString("en-US", EDITION_DATE_FORMAT);

  return (
    <div className="page">
      <div className="masthead">
        <p className="masthead-eyebrow">Real-Time Intelligence &middot; Est. 2026</p>
        <h1 className="masthead-title">FMCG Deal Intelligence</h1>
        <p className="masthead-tagline">
          Mergers, acquisitions &amp; investment activity across the consumer goods industry
        </p>
      </div>

      <div className="dateline-bar">
        <span className="dateline">{today}</span>
        <span className="dateline-divider">&middot;</span>
        <span className="dateline">
          {run ? `Latest edition filed ${new Date(run.created_at).toLocaleString()}` : "No edition on file"}
        </span>
        <div className="dateline-spacer" />
        <ModalStatusBadge />
        <RunButton onClick={handleGenerate} loading={loading} />
      </div>

      {error && (
        <div className="correction-notice">
          <strong>Correction &mdash; run failed:</strong> {error}
        </div>
      )}

      <main className="edition">
        {loading && (
          <div className="printing-notice">
            <div className="printing-spinner" aria-hidden="true" />
            <p>Compiling the latest edition&hellip; scanning wires, checking sources, drafting copy.</p>
          </div>
        )}

        {!loading && run && <NewsletterView run={run} />}

        {!loading && !run && !initialLoad && (
          <div className="empty-front-page">
            <p className="empty-headline">No Edition Has Been Filed Yet</p>
            <p>Click &ldquo;Generate Edition&rdquo; above to run the pipeline and publish the first newsletter.</p>
          </div>
        )}
      </main>

      {run?.id && !loading && (
        <footer className="masthead-footer">
          <DownloadButtons runId={run.id} />
          <p className="colophon">
            Sourced automatically via web search, screened by an LLM for FMCG-deal relevance, and
            checked against a static source-credibility list. See the README for full pipeline details.
          </p>
        </footer>
      )}
    </div>
  );
}
