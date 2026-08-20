import { exportUrl } from "../api";

interface Props {
  runId: string;
}

export default function DownloadButtons({ runId }: Props) {
  return (
    <div className="downloads">
      <span className="downloads-label">Available Formats</span>
      <a href={exportUrl(runId, "csv")}>Raw Data (CSV)</a>
      <span className="downloads-sep">/</span>
      <a href={exportUrl(runId, "json")}>Raw Data (JSON)</a>
      <span className="downloads-sep">/</span>
      <a href={exportUrl(runId, "docx")}>Newsletter (DOCX)</a>
    </div>
  );
}
