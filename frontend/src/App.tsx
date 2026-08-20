import { useEffect, useState } from "react";
import { NewsletterRun, fetchLatest, generateNewsletter } from "./api";
import RunButton from "./components/RunButton";
import NewsletterView from "./components/NewsletterView";
import DownloadButtons from "./components/DownloadButtons";

export default function App() {
  const [run, setRun] = useState<NewsletterRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLatest()
      .then(setRun)
      .catch(() => setRun(null));
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

  return (
    <main>
      <header>
        <h1>FMCG Deal Intelligence</h1>
        <RunButton onClick={handleGenerate} loading={loading} />
      </header>

      {run && (
        <p className="updated-at">
          Last updated: {new Date(run.created_at).toLocaleString()}
        </p>
      )}
      {error && <p className="error">{error}</p>}

      {run ? (
        <>
          <NewsletterView run={run} />
          {run.id && <DownloadButtons runId={run.id} />}
        </>
      ) : (
        !loading && <p>No newsletter generated yet. Click "Generate Newsletter" to run the pipeline.</p>
      )}
    </main>
  );
}
