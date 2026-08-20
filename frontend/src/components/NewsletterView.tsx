import { NewsletterRun } from "../api";

interface Props {
  run: NewsletterRun;
}

export default function NewsletterView({ run }: Props) {
  if (run.status === "failed") {
    return <p className="error">Last run failed: {run.error}</p>;
  }

  if (run.newsletter_sections.length === 0) {
    return <p>No qualifying deal activity found in the latest run.</p>;
  }

  return (
    <div className="newsletter">
      {run.newsletter_sections.map((section) => (
        <section key={section.title}>
          <h2>{section.title}</h2>
          {section.deals.map((deal) => (
            <article key={deal.headline} className="deal">
              <h3>{deal.headline}</h3>
              <p>{deal.summary}</p>
              <p className="meta">
                <strong>Companies:</strong> {deal.companies.join(", ")}
                {deal.deal_amount && (
                  <>
                    {" · "}
                    <strong>Size:</strong> {deal.deal_amount}
                  </>
                )}
              </p>
              <p className="meta">
                <strong>Sources:</strong> {deal.sources.join(", ")}{" "}
                <span className={`tier tier-${deal.credibility_tier}`}>
                  Tier {deal.credibility_tier}
                </span>
              </p>
            </article>
          ))}
        </section>
      ))}
    </div>
  );
}
