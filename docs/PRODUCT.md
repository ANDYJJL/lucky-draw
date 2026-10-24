# Product — finding the pain, then refusing to solve the wrong problem

## The pain, observed not imagined

Lucky Draw started from a repeating scene: two people, a phone full of saved
restaurant posts, and twenty minutes of "I don't know, you pick" before eating
at one of the same three places again.

Watching that scene closely, the failure has three layers:

1. **Collection is easy, retrieval is broken.** Social apps are optimized for
   saving, not for deciding. A saved list sorted by "when you saved it" is
   useless at 6pm on a Friday.
2. **The decider pays a social cost.** Whoever picks the place owns the outcome.
   In couples and group chats, proposing is risk; vetoing is free. So everyone
   vetoes and nobody proposes.
3. **Information isn't the bottleneck.** Ratings, photos, reviews — all abundant.
   What's missing is a *commitment device*: something that ends deliberation
   in a way everyone accepts as fair.

## The insight

**A randomizer is a social technology.** Rock-paper-scissors, drawing straws,
spinning a wheel — groups have always outsourced contested micro-decisions to
chance, because chance can't be blamed and can't play favorites. The product
opportunity wasn't "a better restaurant list." It was to take the saved-post
graveyard people already have, curate it into a deck worth trusting, and let
the deck decide.

That's why Lucky Draw is a deck of cards, not a database with a shuffle button:

- The **fan of cards** on the home screen makes the mechanic legible before
  a single word is read.
- **One big button** ("Draw one") is the entire primary interface.
- The reveal is a **flip with weight** — long enough to feel like an event.

## Decisions that follow from the insight

### Fair rounds, not infinite randomness
Within a round, a card can't repeat; when the deck empties, it reshuffles.
Pure randomness can serve the same place three Fridays in a row and quietly
destroy trust in the deck ("it's rigged / it's broken"). A round structure is
how a physical deck behaves, and it guarantees the long tail of the collection
actually gets played. Redrawing draws the *next* card — it never reshuffles,
because reshuffling on redraw would make "no repeats" a lie.

### Equal odds, no rarity theater
No rare cards, no rarity tiers, no ten-pull bundles. Gacha mechanics optimize
for engagement; this product optimizes for dinner. The moment some places are
"SSR," the unglamorous neighborhood spot nobody posts about — often the best
answer — becomes a booby prize.

### Curation is the product's trust layer
A draw is a recommendation you didn't choose. That only works if every card in
the deck is defensible. So places are added one at a time, sourced from real
local recommendations, then verified: the shop's real name (not the nickname in
the post), the actual address, current hours, a rating from a real platform,
what to order, and one honest caution ("drinks come out slow", "weekend lines").
Production data rules even include: if sources disagree on a shop's name, the
shop's own signage wins. Trust is built in the data, not the UI.

### Designed for two, on purpose
Food decisions in this product's life are made by a couple sharing one account.
So instead of bolting on "social features," the core objects are dual:

- **Two rating slots per place** (1–5 stars + a note each), shown side by side
  on the record card — "Kwan Kitchen: ★5 'the mama noodles!!' / ★4 'great, but
  the mango sticky rice runs salty'".
- **One shared reaction** per place — last word wins, like a real fridge door.
- A **joint food diary**: a calendar of where you actually went and how each
  of you scored it.

The second slot's default name is deliberately neutral ("User 2") — any two
people can share an account, and the product doesn't presume who they are.

### Custom pools: randomness within intent
Pure chance is wrong when a real constraint exists ("nothing spicy tonight",
"only places near Irvine"). Custom pools let you filter the deck first —
cuisine, area, price, rating — then draw. Crucially, when a filter is active,
every count in the UI (the list title, the "Use custom pool (N)" button) refers
to the *filtered* set. What you see is exactly the deck you'll draw from; a
count that quietly means something else is a small lie users feel.

### Bilingual as a first-class citizen
The deck covers LA's Chinese-food heartland; its people live in two languages.
English mode isn't a translated UI shell — the entire dataset (names, dishes,
tips, cautions) has a parallel English edition, search matches both, and the
card faces themselves are re-rendered in English. A feature that only works in
one language would have excluded half the dinner table.

## What success looks like

Not time-in-app. The best session is under thirty seconds: open, draw, argue
happily for one redraw, leave. The metrics that matter are draws per weekend,
redraw rate (healthy disagreement), and how much of the deck has actually been
visited — the diary filling up over months.

## The App Store pitch, in one breath

> Friday night, no plan? Draw a card. 253 hand-picked boba, dessert, food &
> play spots — with must-tries, ratings and tips. Indecision, solved.
