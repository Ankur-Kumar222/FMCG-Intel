import { exportUrl } from "../api";

interface Props {
  runId: string;
}

export default function DownloadButtons({ runId }: Props) {
  return (
    <div className="downloads">
      <a href={exportUrl(runId, "csv")}>Download CSV</a>
      <a href={exportUrl(runId, "json")}>Download JSON</a>
      <a href={exportUrl(runId, "docx")}>Download Newsletter (DOCX)</a>
    </div>
  );
}
