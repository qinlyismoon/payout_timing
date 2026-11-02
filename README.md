# Payout Timing

**Live prototype → https://qinlyismoon.github.io/payout_timing/**

A small, working prototype for marketplace sellers who pay their bills out of Amazon payouts. It answers one question:

> *Will the money I've already earned actually be in my bank before this bill is due?*

All amounts, orders, payments and dates are simulated. The scenario is shifted to your real date, so "today" is always today.

---

## The problem

Since March 2026, Amazon's North American marketplace holds seller funds for 7 days after delivery before they become eligible for payout (DD+7). Sellers in Amazon's own forums describe the result: they track delivery dates by hand, work out release dates, and still can't tell which orders will pay out before a supplier invoice is due.

The information isn't missing — it's scattered across the marketplace, accounting tools and the bank, and none of them connect it to a specific decision. Payout Timing does that one thing: it lines up every pending dollar against every upcoming bill.

## Try it (2 minutes)

1. **Cash outlook.** The day strip shows money arriving (top) and your bank balance (bottom). Each upcoming payment is a dot. Hover a dot to see what can and can't arrive before it.
2. **Open "Supplier final payment".** The bar splits the $5,000 into what you can rely on, what's uncertain, and what's missing.
3. **Close the gap.** In *What could close the gap*, drag the *Eligible* payout earlier, drag the payment later (this payee accepts changes), or add your own cash. The result updates as you drag.
4. **Confirm a step.** Tick a step in *Your steps* once you've actually done it. Head back to the overview — your plan is shown there too.
5. **Footer → Preview "All covered"** to see the calm state.

## Design decisions, briefly

- **Known, estimated, unknown.** Every amount is exactly one kind: green (in the bank), amber (date can be worked out from a stated rule, always shown as a range), grey hatch (on hold, never counted). Red is reserved for a shortfall.
- **Never add known and estimated money into one total.** The bank balance and money on its way are separate numbers.
- **Understand before acting.** Each screen shows the situation first. The drag-to-plan tool comes after.
- **Only make draggable what the user controls.** Payout request day: yes. Own cash: when you send it and how much. A due date: only if the payee accepts changes. A payout already sent or a hold: never.
- **Dragging is a simulation; ticking is a fact.** A plan stays a plan until you confirm each step.
- **No financing advice.** The tool models any cash you add; it never names lenders or products.

The full working rules (visual language, collision rules, motion, ship checklist) are in [`docs/DESIGN.md`](docs/DESIGN.md).

## How the dates are worked out

```
Delivered → +7 days (DD+7) → next payout (every 14 days) → +3–5 business days → in your bank
```

These are the prototype's stated assumptions, not Amazon's exact schedule. Holds have no date and are never counted.

## What's real and what isn't

| | |
|---|---|
| **Based on public evidence** | The DD+7 rule change and seller complaints about cash flow and visibility (Amazon Seller Forums, EcommerceBytes, Shopify Community). |
| **Design assumptions** | That sellers need a bill-by-bill view rather than more payout statuses; that drag-to-plan helps them decide. Not yet tested with sellers. |
| **Simulated** | Every order, amount, payee and date. No real marketplace or bank connection. |
| **Not built** | Real data import, notifications, multi-currency, other marketplaces. |

## Stack

- One static `index.html`: HTML, CSS and vanilla JavaScript. No framework, no build step, no dependencies besides Google Fonts (Inter, JetBrains Mono).
- Animation uses CSS transitions, FLIP for list and block moves, and the View Transitions API where the browser supports it.
- Deployed with GitHub Pages via GitHub Actions.

**AI tools.** Claude and ChatGPT were used to search for first-hand evidence in parallel and to critique each other's shortlists; the direction and every judgment call were mine. The prototype was built with Claude as a coding partner against the rules in `docs/DESIGN.md`, which I wrote and revised after each review round. Changes were reviewed with screenshots at four widths and an overlap check on labels and chips.

## Overlap check

`tools/collide.py` measures every visible label, chip, dot, tooltip and reference line in the day strips at 1000, 1100 and 1280px — overview at rest, overview with each payment hovered, and each payment page — and lists any pair whose boxes intersect.

The original checker was lost with the build session, so this is a rewrite from the spec in `docs/DESIGN.md` §5. It measures text by its rendered glyph boxes and respects stacking (a line that runs behind an opaque chip doesn't count). Current result: **0 overlaps across all 27 states.**

The first run of the rewrite found three real issues in the overview's hover state, now fixed: the hover tooltip covered the next payment dot and the peak balance label (its content moved to the footer result, so nothing is drawn on top of the strip), and the hover line crossed the "Payout sent" label (chips now sit above the line).

```bash
pip install playwright && playwright install chromium
python3 -m http.server 8000 &
python3 tools/collide.py http://localhost:8000/
```

## Run locally

```bash
git clone https://github.com/qinlyismoon/payout_timing.git
cd payout_timing
python3 -m http.server 8000   # then open http://localhost:8000
```

Opening `index.html` directly also works.

---

Made for a Design Engineer challenge. Illustrative prototype — not financial advice.
