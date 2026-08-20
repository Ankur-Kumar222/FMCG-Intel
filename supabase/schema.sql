create table if not exists newsletter_runs (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now(),
    query_set jsonb not null default '[]',
    raw_articles jsonb not null default '[]',
    deduped_count integer not null default 0,
    relevant_articles jsonb not null default '[]',
    newsletter_markdown text not null default '',
    newsletter_sections jsonb not null default '[]',
    status text not null default 'running',
    error text
);

create index if not exists newsletter_runs_created_at_idx
    on newsletter_runs (created_at desc);
