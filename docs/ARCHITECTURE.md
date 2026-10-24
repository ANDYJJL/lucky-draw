# Architecture — one file, local-first, paranoid about your data

## The single-file bet

The entire application — markup, styles, state management, i18n, sync — is one
HTML file (~6,700 lines, no framework, no build step). This is a choice, not a
limitation:

- **Zero toolchain rot.** There is nothing to `npm install` in three years.
  The file that ships is the file you read.
- **Deploy = upload one zip.** Static hosting (Cloudflare Pages) serves it;
  there is no server to patch.
- **Performance by default.** No framework runtime, no hydration. First paint
  is HTML and CSS; the JS is one classic script.

The cost — discipline. Shared display data tends to grow multiple consumers
(the draw stage's card-back text is written by two different renderers), and
the rule learned the hard way is: *grep every consumer before you patch one.*
A fix that only reaches one renderer ships an inconsistent UI.

## Data model

Two layers, deliberately separate:

1. **The deck (static, editorial).** Places are baked into the page as a JSON
   array (plus a parallel `PLACES_EN` object and a per-place meta map). The
   deck changes by publishing a new build, like a magazine issue — fitting a
   curated product.
2. **The people's layer (dynamic, personal).** Ratings, notes, reactions,
   visit records, custom pools and UI prefs belong to the users and live in
   Supabase (Postgres + Auth), synced per account.

Editorial source data is kept in a richer schema (`data/places.sample.json`)
and compiled into the page's runtime format by the release pipeline — the page
never ships fields it doesn't render.

## Images at scale

253 places × (card face, atlas tile, hero) in two languages outgrew any single
static deploy, so images are sharded across multiple static projects (cards,
cards-EN, tiles) on the same CDN, with the main file pointing at each shard.
Card faces are *rendered*, not designed one by one: a Python pipeline
(`tools/make_card.py`, and an auto-fitting English edition) draws the
1080×1440 face from structured data — hero photo cover-cropped into the face,
one accent, fixed hierarchy, and a **width audit** that fails the build if any
line would overflow.

## Local-first state & sync

- Everything works signed-out, stored on-device (draw rounds and history live
  in local storage; the draw must never wait for a network).
- On sign-in, personal data syncs to the account. UI prefs sync as one
  versioned blob; ratings do **not** trust the blob (below).

## The incident that designed the sync layer

An early version had a classic local-first bug: a phone whose PWA storage was
empty (iOS keeps web-app and browser storage in separate partitions) signed in
and *uploaded its emptiness*, wiping the account's ratings and notes. The fix
became a small constitution for this codebase:

1. **Saved records are the highest priority.** No feature ships if it can lose
   them.
2. **Ratings write through.** A score is written directly to its database
   table at the moment it's given; the synced blob is demoted to a cache.
3. **Merges are unions, never replacements.** Sync combines local and remote
   by record id; deletions travel as explicit tombstones, so "absent" never
   silently means "deleted."
4. **Login reconciles.** On sign-in, the client compares its cache against the
   authoritative table and repairs gaps before the user can notice.

Dual-slot ratings live in `visit_ratings` (one row per place per slot), which
also powers the diary calendar: a visit is a dated row with both scores.

## Internationalization

Language is a data problem, not a strings problem. The UI dictionary covers
chrome text, but the deck itself is content: at boot (and on every language
switch) `applyPlaceLang()` swaps each place's display fields — name, must-try
list, note, caution, price, hours, even the search keywords — from the parallel
English edition, keeping originals aside for the swap back. Cuisine and region
labels translate through small meta maps. Because card faces are images, the
English edition has its own rendered set, selected by the same swap.

## Failure honesty

- If the custom layer fails to load, the static deck still draws — sync is an
  enhancement, never a dependency of the core ritual.
- The app's "is it live?" checks are done against the *rendered page*, not
  HTTP status: a deploy isn't done until the real UI shows it.
