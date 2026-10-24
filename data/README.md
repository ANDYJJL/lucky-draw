# Data

`places.sample.json` is the editorial source data for the 12 sample places —
the same richer schema the production deck is curated in (cuisine in
`category`, full address / hours / phone / source fields).

The app itself runs on a compiled, slimmer format baked into
`app/index.html`: each place keeps only the fields the UI renders, grouped by
a `pool` field (`boba` / `dessert` / `food` / `play`), and ids are shortened
where the editorial id carries a location suffix — e.g. editorial
`kwan-kitchen-pasadena` is `kwan-kitchen` in the app, which is also the base
name of its card images in `app/assets/`.

The full production dataset (253 places) is intentionally not in this
repository; see "What's intentionally not in this repo" in the main README.
