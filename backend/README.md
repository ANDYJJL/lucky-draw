# Backend — Supabase

Lucky Draw has no server of its own. Its backend is a Supabase project
(Postgres + Auth + Storage) that the single-file app in `app/` talks to
directly over the REST API — the client ships its own small REST layer
instead of the supabase-js library (see the sync notes in
`docs/ARCHITECTURE.md`).

## Files

- `schema.sql` — the complete, sanitized schema: tables, grants, row-level
  security, the `create_space` / `join_space` RPCs, the new-user trigger,
  and the public `avatars` storage bucket with its policies. No project
  URLs, keys or personal data.

## Set it up

1. Create a project at [supabase.com](https://supabase.com).
2. SQL Editor → paste `schema.sql` → Run.
3. In `app/index.html`, set `SB_URL` and `SB_ANON_KEY` to your project's
   values (shape documented in `.env.example`). The anon key is a public
   client key — row-level security is what protects the data. Never put a
   `service_role` key in client code.
4. Optional, to match production auth behaviour: Authentication → Providers
   → Email → turn **Confirm email** off, so sign-up signs you in directly.

## Tables at a glance

| Table | What it holds |
|---|---|
| `profiles` | One row per user: display name, avatar URL, versioned `prefs` JSON blob (UI prefs, custom pools, draw history, ratings cache) |
| `spaces` | A shared container (name + invite code) |
| `space_members` | Who belongs to which space |
| `visits` | One record per visit: space, place slug, optional date |
| `visit_ratings` | Authoritative dual-slot ratings — one row per (visit, slot), written through at rating time and reconciled on sign-in |
| `avatars` (storage bucket) | `<uid>/avatar.jpg`, `<uid>/background.jpg`, public read, owner-only write |

A legacy `ratings` table existed in an early design and is not used by the
current client; ratings moved to the prefs blob and then to
`visit_ratings`. It is intentionally not part of this schema.
