-- Run manually in the Supabase SQL Editor after creating a free project.
-- This table is intended for server-side access using SUPABASE_SERVICE_ROLE_KEY.
-- RLS is enabled and no anon/authenticated policies are granted.
create table if not exists public.dashboard_drafts (
    id text primary key,
    draft jsonb not null,
    review_status text not null default 'pending_review'
        check (review_status in (
            'pending_review',
            'approved_for_manual_next_step',
            'rejected'
        )),
    reviewer_note text not null default '',
    published boolean not null default false check (published = false),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.dashboard_drafts enable row level security;

-- Deliberately create no policies for anon or authenticated clients.
-- The server-side service role bypasses RLS; never expose its key to browsers.
grant all on table public.dashboard_drafts to service_role;
