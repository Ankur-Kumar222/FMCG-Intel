import { CredibilityTier, NewsletterRun } from "../api";

interface Props {
  run: NewsletterRun;
}

const TIER_LABEL: Record<CredibilityTier, string> = {
  A: "Verified Source",
  B: "Trade Press",
  C: "Unverified",
};

function stat(label: string, value: number | string) {
  return (
    <div className="stat-box" key={label}>
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

export default function NewsletterView({ run }: Props) {
  if (run.status === "failed") {
    return (
      <div className="correction-notice standalone">
        <strong>This edition failed to publish.</strong>
        <p>{run.error}</p>
      </div>
    );
  }

  return (
    <>
      <div className="stats-strip">
        {stat("Articles Scanned", run.raw_articles.length)}
        {stat("After De-duplication", run.deduped_count)}
        {stat("Confirmed FMCG Deals", run.relevant_articles.length)}
        {stat("Search Queries Run", run.query_set.length)}
      </div>

      {run.newsletter_sections.length === 0 ? (
        <div className="empty-front-page">
          <p className="empty-headline">No Qualifying Deal Activity Found</p>
          <p>The wires were quiet this run &mdash; no FMCG deals cleared the relevance bar.</p>
        </div>
      ) : (
        <div className="newsletter">
          {run.newsletter_sections.map((section, sectionIdx) => (
            <section className="news-section" key={section.title}>
              <h2 className="section-heading">
                <span>{section.title}</span>
              </h2>
              <div className="deals-grid">
                {section.deals.map((deal, dealIdx) => (
                  <article
                    className={`deal-card${sectionIdx === 0 && dealIdx === 0 ? " lead-story" : ""}`}
                    key={deal.headline}
                  >
                    <h3 className="deal-headline">{deal.headline}</h3>
                    <p className="deal-summary">{deal.summary}</p>
                    <dl className="deal-facts">
                      <div>
                        <dt>Companies</dt>
                        <dd>{deal.companies.join(" · ")}</dd>
                      </div>
                      <div>
                        <dt>Deal Type</dt>
                        <dd className="capitalize">{deal.deal_type}</dd>
                      </div>
                      {deal.deal_amount && (
                        <div>
                          <dt>Deal Size</dt>
                          <dd>{deal.deal_amount}</dd>
                        </div>
                      )}
                    </dl>
                    <div className="deal-sources">
                      <span className={`credibility-badge tier-${deal.credibility_tier}`}>
                        {TIER_LABEL[deal.credibility_tier]}
                      </span>
                      <span className="source-list">{deal.sources.join(", ")}</span>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </>
  );
}
