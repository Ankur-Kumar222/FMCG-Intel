interface Props {
  onClick: () => void;
  loading: boolean;
}

export default function RunButton({ onClick, loading }: Props) {
  return (
    <button onClick={onClick} disabled={loading}>
      {loading ? "Generating…" : "Generate Newsletter"}
    </button>
  );
}
