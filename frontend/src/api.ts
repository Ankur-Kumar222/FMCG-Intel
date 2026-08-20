export type CredibilityTier = "A" | "B" | "C";

export interface Article {
  title: string;
  url: string;
  source_domain: string;
  credibility_tier: CredibilityTier | null;
  is_relevant: boolean | null;
  deal_type: string | null;
  companies: string[];
  deal_amount: string | null;
  one_line_summary: string | null;
  also_reported_by: string[];
}

export interface NewsletterDeal {
  headline: string;
  companies: string[];
  deal_type: string;
  deal_amount: string | null;
  summary: string;
  sources: string[];
  credibility_tier: CredibilityTier;
}

export interface NewsletterSection {
  title: string;
  deals: NewsletterDeal[];
}

export interface NewsletterRun {
  id: string;
  created_at: string;
  query_set: string[];
  raw_articles: Article[];
  deduped_count: number;
  relevant_articles: Article[];
  newsletter_markdown: string;
  newsletter_sections: NewsletterSection[];
  status: "running" | "success" | "failed";
  error: string | null;
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${await res.text()}`);
  }
  return res.json();
}

export function fetchLatest(): Promise<NewsletterRun> {
  return fetch("/api/latest").then((res) => handle<NewsletterRun>(res));
}

export function generateNewsletter(): Promise<NewsletterRun> {
  return fetch("/api/generate", { method: "POST" }).then((res) => handle<NewsletterRun>(res));
}

export function exportUrl(runId: string, format: "csv" | "json" | "docx"): string {
  return `/api/runs/${runId}/export?format=${format}`;
}
