-- Falmouth Wellness Discovery
-- Project: james-sites (https://oiousqgzqcjanikglkxl.supabase.co)
-- Run this in the Supabase SQL editor.
--
-- Anonymous visitors may INSERT a signup or a partner inquiry.
-- They cannot SELECT, UPDATE, or DELETE. Do not add a public SELECT policy.
-- The site sends Prefer: return=minimal so PostgREST does not try to read the row back.

create extension if not exists pgcrypto;

create table if not exists public.magazine_reader_signups (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  full_name text not null,
  email text not null,
  delivery text not null check (delivery in ('digital', 'print')),
  street_address text,
  city text,
  postal_code text,
  partner_location text,
  interests text[] not null default '{}',
  consent boolean not null,
  user_agent text,
  constraint magazine_reader_signups_consent check (consent = true),
  constraint magazine_reader_signups_print_address check (
    delivery <> 'print'
    or (
      length(btrim(coalesce(street_address, ''))) > 0
      and length(btrim(coalesce(city, ''))) > 0
    )
  )
);

create table if not exists public.magazine_partner_inquiries (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  business_name text not null,
  contact_name text not null,
  email text not null,
  phone text,
  category text,
  package text,
  gift_cards boolean not null default false,
  message text,
  consent boolean not null,
  user_agent text,
  constraint magazine_partner_inquiries_consent check (consent = true)
);

create index if not exists magazine_reader_signups_created_at_idx
  on public.magazine_reader_signups (created_at desc);

create index if not exists magazine_partner_inquiries_created_at_idx
  on public.magazine_partner_inquiries (created_at desc);

alter table public.magazine_reader_signups enable row level security;
alter table public.magazine_partner_inquiries enable row level security;

revoke all on table public.magazine_reader_signups from public, anon, authenticated;
revoke all on table public.magazine_partner_inquiries from public, anon, authenticated;

grant insert on table public.magazine_reader_signups to anon, authenticated;
grant insert on table public.magazine_partner_inquiries to anon, authenticated;

drop policy if exists "anonymous insert reader signups" on public.magazine_reader_signups;
create policy "anonymous insert reader signups"
  on public.magazine_reader_signups
  for insert
  to anon, authenticated
  with check (consent = true);

drop policy if exists "anonymous insert partner inquiries" on public.magazine_partner_inquiries;
create policy "anonymous insert partner inquiries"
  on public.magazine_partner_inquiries
  for insert
  to anon, authenticated
  with check (consent = true);

-- Intentionally no SELECT, UPDATE, or DELETE policies.
-- Read these tables from the Supabase dashboard or with the service role.
