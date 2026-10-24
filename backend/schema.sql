-- Lucky Draw — Supabase backend schema (sanitized, for reference)
-- =====================================================================
-- This file reconstructs the database the app in app/index.html talks to:
-- the same tables, row-level security shape, RPCs and storage bucket the
-- production deployment uses, with every project-specific value removed.
-- There are no project URLs, keys, user ids or personal data in here.
--
-- How to use: create a fresh Supabase project, open the SQL Editor, paste
-- this whole file and run it once. Then set SB_URL / SB_ANON_KEY in
-- app/index.html (see .env.example) and, if you want the production auth
-- behaviour, turn OFF "Confirm email" (email + password, sign-up = signed in).
--
-- Data model in one paragraph: the deck itself is static (baked into the
-- page). Everything personal lives here — profiles (display name, avatar,
-- a versioned prefs blob), spaces + space_members (a shared container two
-- people join), visits (one dated — or undated — record per place visit),
-- and visit_ratings (one row per visit per rating slot, written through at
-- rating time; see docs/ARCHITECTURE.md for why ratings do not live in the
-- prefs blob).

-- ---------------------------------------------------------------------
-- Extensions
-- ---------------------------------------------------------------------
create extension if not exists pgcrypto;  -- gen_random_uuid()

-- ---------------------------------------------------------------------
-- profiles — one row per auth user
-- prefs is a versioned JSON blob: { v, ui, pools, gacha, archive, updatedAt }
-- ---------------------------------------------------------------------
create table if not exists public.profiles (
  id           uuid primary key references auth.users (id) on delete cascade,
  display_name text,
  avatar_url   text,
  prefs        jsonb,
  created_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------------
-- spaces / space_members — the shared container (invite code is kept from
-- the original two-account design; the shipped product uses one shared
-- account, but the schema keeps the general shape)
-- ---------------------------------------------------------------------
create table if not exists public.spaces (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  invite_code text not null unique,
  created_by  uuid references public.profiles (id) on delete set null,
  created_at  timestamptz not null default now()
);

create table if not exists public.space_members (
  space_id   uuid not null references public.spaces (id) on delete cascade,
  user_id    uuid not null references public.profiles (id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (space_id, user_id)
);

-- ---------------------------------------------------------------------
-- visits — one record per visit. visited_on is deliberately nullable:
-- "we ate there, but nobody remembers which day" is a real case.
-- place_id is the deck's slug (e.g. 'bopomofo-cafe'), not a foreign key —
-- the deck is editorial data baked into the page, not a table.
-- ---------------------------------------------------------------------
create table if not exists public.visits (
  id         uuid primary key default gen_random_uuid(),
  space_id   uuid not null references public.spaces (id) on delete cascade,
  place_id   text not null,
  visited_on date,
  created_by uuid references public.profiles (id) on delete set null,
  created_at timestamptz not null default now()
);
create index if not exists visits_space_idx on public.visits (space_id, visited_on desc, created_at desc);

-- ---------------------------------------------------------------------
-- visit_ratings — dual-slot ratings, the authoritative rating store.
-- One row per (visit, slot); slot 1 and 2 are the two people on the
-- account. score/note are nullable so a slot can hold only a note.
-- The client upserts on conflict (visit_id, slot) at rating time and
-- reconciles against this table on sign-in.
-- ---------------------------------------------------------------------
create table if not exists public.visit_ratings (
  visit_id   uuid not null references public.visits (id) on delete cascade,
  slot       smallint not null check (slot in (1, 2)),
  score      smallint check (score between 1 and 5),
  note       text,
  updated_at timestamptz not null default now(),
  primary key (visit_id, slot)
);

-- ---------------------------------------------------------------------
-- Grants — from 2026-10-30 Supabase no longer auto-grants Data API access
-- to new tables, so ship the grants with the migration. RLS (below) still
-- decides which rows each caller can actually touch.
-- ---------------------------------------------------------------------
grant select, insert, update, delete on public.profiles      to authenticated;
grant select, insert, update, delete on public.spaces         to authenticated;
grant select, insert, update, delete on public.space_members to authenticated;
grant select, insert, update, delete on public.visits         to authenticated;
grant select, insert, update, delete on public.visit_ratings to authenticated;
grant all on all tables in schema public to service_role;

-- ---------------------------------------------------------------------
-- Row-level security
-- Helper: does the current user share the given space?
-- ---------------------------------------------------------------------
alter table public.profiles      enable row level security;
alter table public.spaces        enable row level security;
alter table public.space_members enable row level security;
alter table public.visits        enable row level security;
alter table public.visit_ratings enable row level security;

create or replace function public.is_space_member(p_space_id uuid)
returns boolean
language sql stable security definer set search_path = public
as $$
  select exists (
    select 1 from public.space_members
    where space_id = p_space_id and user_id = auth.uid()
  );
$$;

-- profiles: read your own row, plus the profiles of people who share a
-- space with you (the client loads co-member names/avatars); write only
-- your own row.
drop policy if exists profiles_select on public.profiles;
create policy profiles_select on public.profiles for select to authenticated
  using (
    id = auth.uid()
    or exists (
      select 1 from public.space_members mine
      join public.space_members theirs on theirs.space_id = mine.space_id
      where mine.user_id = auth.uid() and theirs.user_id = profiles.id
    )
  );
drop policy if exists profiles_insert on public.profiles;
create policy profiles_insert on public.profiles for insert to authenticated
  with check (id = auth.uid());
drop policy if exists profiles_update on public.profiles;
create policy profiles_update on public.profiles for update to authenticated
  using (id = auth.uid()) with check (id = auth.uid());

-- spaces: members can read their space. Creation/joining go through the
-- security-definer RPCs below, so there is no direct insert policy.
drop policy if exists spaces_select on public.spaces;
create policy spaces_select on public.spaces for select to authenticated
  using (public.is_space_member(id));

-- space_members: members can see who is in their space and leave it
-- (delete their own row).
drop policy if exists space_members_select on public.space_members;
create policy space_members_select on public.space_members for select to authenticated
  using (public.is_space_member(space_id));
drop policy if exists space_members_delete on public.space_members;
create policy space_members_delete on public.space_members for delete to authenticated
  using (user_id = auth.uid());

-- visits: full access for members of the visit's space; you stamp your
-- own id as created_by on insert.
drop policy if exists visits_select on public.visits;
create policy visits_select on public.visits for select to authenticated
  using (public.is_space_member(space_id));
drop policy if exists visits_insert on public.visits;
create policy visits_insert on public.visits for insert to authenticated
  with check (public.is_space_member(space_id) and created_by = auth.uid());
drop policy if exists visits_delete on public.visits;
create policy visits_delete on public.visits for delete to authenticated
  using (public.is_space_member(space_id));

-- visit_ratings: access follows the parent visit's space membership.
drop policy if exists visit_ratings_all on public.visit_ratings;
create policy visit_ratings_all on public.visit_ratings for all to authenticated
  using (
    exists (select 1 from public.visits v
            where v.id = visit_ratings.visit_id and public.is_space_member(v.space_id))
  )
  with check (
    exists (select 1 from public.visits v
            where v.id = visit_ratings.visit_id and public.is_space_member(v.space_id))
  );

-- ---------------------------------------------------------------------
-- RPCs used by the client: sb.rpc("create_space", { p_name })
--                          sb.rpc("join_space",   { p_code })
-- ---------------------------------------------------------------------
create or replace function public.create_space(p_name text)
returns uuid
language plpgsql security definer set search_path = public
as $$
declare
  v_id uuid;
  v_code text;
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  v_code := upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8));
  insert into public.spaces (name, invite_code, created_by)
  values (coalesce(nullif(trim(p_name), ''), 'Our food diary'), v_code, auth.uid())
  returning id into v_id;
  insert into public.space_members (space_id, user_id) values (v_id, auth.uid());
  return v_id;
end;
$$;

create or replace function public.join_space(p_code text)
returns uuid
language plpgsql security definer set search_path = public
as $$
declare
  v_id uuid;
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  select id into v_id from public.spaces where invite_code = upper(trim(p_code));
  if v_id is null then raise exception 'space not found'; end if;
  insert into public.space_members (space_id, user_id) values (v_id, auth.uid())
  on conflict do nothing;
  return v_id;
end;
$$;

grant execute on function public.create_space(text) to authenticated;
grant execute on function public.join_space(text)   to authenticated;

-- ---------------------------------------------------------------------
-- New-user trigger: every auth user gets a profiles row automatically
-- (the client also inserts defensively if the row is missing).
-- ---------------------------------------------------------------------
create or replace function public.handle_new_user()
returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  insert into public.profiles (id) values (new.id) on conflict do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------------------------------------------------------------------
-- Storage: public "avatars" bucket. Objects live at <uid>/avatar.jpg and
-- <uid>/background.jpg; reads are public, writes are owner-only.
-- ---------------------------------------------------------------------
insert into storage.buckets (id, name, public)
values ('avatars', 'avatars', true)
on conflict (id) do nothing;

drop policy if exists avatars_public_read on storage.objects;
create policy avatars_public_read on storage.objects for select
  using (bucket_id = 'avatars');
drop policy if exists avatars_owner_insert on storage.objects;
create policy avatars_owner_insert on storage.objects for insert to authenticated
  with check (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists avatars_owner_update on storage.objects;
create policy avatars_owner_update on storage.objects for update to authenticated
  using (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists avatars_owner_delete on storage.objects;
create policy avatars_owner_delete on storage.objects for delete to authenticated
  using (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text);
