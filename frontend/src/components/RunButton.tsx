interface Props {
  onClick: () => void;
  loading: boolean;
  disabled: boolean;
  disabledReason?: string;
}

export default function RunButton({ onClick, loading, disabled, disabledReason }: Props) {
  return (
    <span className="run-button-wrap" title={disabled && !loading ? disabledReason : undefined}>
      <button className="run-button" onClick={onClick} disabled={loading || disabled}>
        {loading ? "Printing…" : "Generate Edition"}
      </button>
    </span>
  );
}
