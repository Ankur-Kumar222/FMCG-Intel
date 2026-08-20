interface Props {
  onClick: () => void;
  loading: boolean;
}

export default function RunButton({ onClick, loading }: Props) {
  return (
    <button className="run-button" onClick={onClick} disabled={loading}>
      {loading ? "Printing…" : "Generate Edition"}
    </button>
  );
}
