# Payout Timing — Design rules

Working rules for the prototype. Every change is checked against this file before it ships.

## 1. Product principles

1. **Known, estimated, unknown.** Every amount belongs to exactly one kind, and the kind is shown by color, never by a second label system.
   - Known (green): already in the bank.
   - Estimated (amber): date can be worked out from a stated rule; always shown as a range.
   - Unknown (grey, hatched): no date can be worked out; never counted. Grey, not red: red is reserved for a shortfall, which is a result, while a hold is only missing information.
2. **Dates follow the real today.** The scenario is shifted to the viewer's date. Bills are placed relative to the Amazon fund windows (in business days), so the story and every amount are the same on any weekday, and no two bills share a day.
3. **Facts before forecasts.** "Your money now" is not limited to the 14-day window. Only the payment forecast is.
4. **Understand before acting.** A screen first shows the situation (how much, by when, why). Interactive "what if" tools come after the situation is clear, never as the first thing a user sees.
5. **Only make draggable what the user controls.** The day an eligible or released payout is requested (the block is the arrival range that follows, moved one day at a time with a soft magnetic pull). Own cash is not dragged: it is pinned to the deadline and only its amount changes. A payment's due date is set by the payee: it is draggable only when the data says the payee accepts changes (`negotiable`), and then only as a single day, business days only, with "needs their OK" shown. Otherwise it is locked. Never the timing of a payout already sent, never a hold.
6. **No financing recommendations.** The tool models any cash the user adds; it never names or compares lenders or products.

## 2. Visual language

- Top bar: brand on the left, today's date on the right, same width as the page content. No breadcrumb (two levels only); the detail page has one back link. Demo controls (scenario preview, simulated-data note) live in the page footer, never in the top bar.

- Ground: cool neutral `--bg`; surfaces white; hairline borders; one accent (deep teal) for titles, focus and selection.
- Type: one sans family; weights 400/500/600 for text, 700 only for money inside chips. Numbers use tabular figures.
- Hierarchy of money: bank balance is the largest number on the overview; money on its way is one step smaller and lighter. Never add known and estimated money into one total.
- Shortfall is written as `−$1,500` in the shortfall color. When a later payment carries an earlier gap, show its own gap first and the carried amount as a second, smaller line.
- Dates: relative ("Due in 6 days") with a clock icon where urgency matters; absolute short dates ("Nov 4–6") inside the calendar. Month names appear only on the first visible day and on the 1st of a month.
- Today: filled teal circle around the date number.
- Chart legend explains the payment dots (Covered / At risk / Short), not the money colours already defined above it.
- The overview strip has two zones divided by a line: money arriving (top, the only part greyed when a deadline is shown) and bank balance (bottom).
- Dates in lists are calendar tiles (month over day number), all the same style: teal month header, white day. Urgency is carried by "due in N days" and the status, not by an extra colour threshold.
- Weekends: one rounded neutral band per Sat–Sun pair, running the full height of the day grid. This is the only full-height band.

- Pills are only for payment status (Covered / At risk / Short), the verdict. Per-fund timing ("Before the deadline?") is a reason, written as icon + plain text, never a pill. One icon per meaning, all in a circle: clock = may be in time (already on its way), arrow back to a bar = only if paid out early (needs you to act), cross = too late, dashed circle = not counted.
- Payment status rule: Covered = enough even if Amazon money is late (worst case); At risk = enough if Amazon money lands in time (expected case); Short = not enough even then. Only Short shows an amount, always. The line under the pill says what would fix it ("Paying out early would cover it") or that nothing on time would.
- Tables use fixed column widths so switching scenarios never moves columns.

## 3. The day strip (shared by overview and payment page)

The same component appears on both pages so the user carries one mental model.

Layout from top to bottom:
1. Month row (labels centered on their column).
2. Weekday + date row.
3. Money in: one lane per fund category, in arrival order. A category in the "No date" zone may share a lane with a dated category, because the zones never overlap horizontally.
4. Dashed separator.
5. Money out: payments as point markers, centered on their due day, sized to their content. A payment is a moment, not a span.
6. Footer row: running total, right-aligned to the end of the day it is reached, with a short tick in the footer only.

Interaction (overview): the payments list does not repeat what the chart shows; its shortfall sits next to the status chip. Hovering a table row does not touch the chart (it is out of view). Pointing at or focusing a payment dot marks its row, enlarges the dot, draws the cash-needed-by line, fades the money that can't arrive before it (no hatched veil), outlines money that might, draws the cash deadline line and a veil over everything after it; the footer swaps its totals for that payment's result. No text is ever drawn on top of the strip.

## 4. Collision rules (check every time)

- No text may overlap other text, a chip, a band edge, or a line. If two labels can meet, one of them moves or is removed.
- Labels anchored to a day end at that day's right edge (right-aligned) or start at its left edge; never centered across a boundary into another zone (for example, into "No date").
- Balance labels are measured and placed in order of importance (lowest point first); a label that would touch another label or a payment dot flips to the other side of the line, or is dropped.
- Chips keep at least 4px from column edges, 8px between stacked chips, and 12px from the "No date" divider.
- Only weekend bands span the full grid height. Any other emphasis (milestones, deadlines) lives in the header or footer, or is a 2px line with no attached label inside the grid.
- Point events (payments) are centered on their day. Range events (arrivals) span their days.
- Phone width: the strip scrolls inside its own container; the page never scrolls sideways.

## 5. Ship checklist

1. Script runs with no console errors.
2. Numbers match across banner, strip, list and payment page.
3. Screenshots taken at 1000px, 1100px, 1280px and 390px, for: overview at rest, overview with a payment hovered, payment page at rest, payment page with a plan applied, and the "All covered" state.
4. Run the overlap check (`collide.py`): it measures every label, chip, tick and footer item at 1000, 1100 and 1280px, at rest and while each payment is hovered, and lists any pair whose boxes intersect. It must report zero, apart from layers that cross-fade in the same spot by design.
5. Each screenshot reviewed against section 4 before publishing.
6. Labels whose position depends on width (payment names under the balance chart) are laid out from measured text widths, and the strip re-lays out on resize.

## 6. Detail page head

- The bar is the payment itself (its amount = 100%). Earlier payments take their share first and are named in the text, never folded into a bigger "needed" number.
- Three parts, same structure each (label, amount, one line of why): Can rely on (green), Uncertain (amber, which payout and when it lands vs the deadline), Missing (red hatch, which funds land too late or are on hold, and whether paying out early would cover it).

## 7. Plan: simulate, then confirm

- Dragging is a simulation. Each step in "Your steps" has a check: ticking it means the user actually did it (requested the payout, the payee agreed, the cash was added). A done step locks its block and shows a check.
- A moved block leaves a dashed outline where it started, on the payment page and on the overview strip. The overview says "Includes your plan · n of m steps done" and a moved payment shows "Planned / Agreed: moved from …".
- Moving a block back to where it started removes the step. Reset sits in the "Your steps" header.
- Drag handle: two short vertical bars. The banner bell keeps ringing, with a ring going out, for as long as it is hovered.

## 8. Plan details (round 3)

- Own cash is a bank transfer (1–2 business days). You drag the day you send it; the block runs from that send day to the last landing day, with the same text as Amazon blocks (amount + landing dates), and it counts as sure / maybe / late against the deadline. Default send day is the latest one that still lands by the deadline. The step reads "Send [$amount] from your own account" on the send day.
- Gutter: lane name plus one plain line of what you can do ("Drag to pick payout day", "Already sent", "Drag to ask for later", "Due date fixed"). No icon chips.
- The result row has a fixed height. When moving the payment puts other bills ahead of it, that is said on the payment step itself ("Contractor ($400) would then be paid first"), not as a floating note.
- Rebuilds glide: blocks, labels, tracks and the steps list move with FLIP (320 ms), the grid height eases, a new lane fades/slides in. A drag always ends, even if the pointer is lost.
- "How these dates are worked out" explains durations, not today's dates: Delivered → +7 days → next payout (every 14 days) → +3–5 business days, then the rules. It opens by height with the content fading in; one animation clock drives both the panel height and the page scroll on the same ease-out curve (420 ms open, 300 ms close), so the page follows the panel smoothly and the panel ends fully in view.
- Overview plan indicator is a compact chip "Plan n/m" (full sentence in the tooltip).
- Opening a payment: chevron nudges and the name turns accent on hover; on click the row grows into the page header (View Transitions, cross-fade fallback), and back reverses it.

## 9. Certainty and confirmation (round 4)

- A plan result says how sure it is: "For sure, even if Amazon money is late" or "Only if $X lands by <deadline>".
- No separate certainty box. The uncertain funds are already visible as blocks crossing the deadline. "+ Add your own cash" pre-fills the worst-case amount when only the expected case is covered (a buffer).
- Confirming arrival lives on the fund's own row in "Where the money comes from", and only once its landing window has started ("Landed? Confirm it"); before that the row just says from which day it can be confirmed. A confirmed fund becomes bank money everywhere.
- Motion scope: a drag never rebuilds the section; only the moved block settles, its start outline fades in, and the steps list changes. Rows that stay keep their place across rebuilds; only new rows animate.
- Your steps: no "tick when done" filler. Each step has a useful second line (lands when / needs their agreement / transfer time). Own cash amount is typed inline. Rows are sorted by date; on change rows glide (FLIP) and new rows rise in one after another.
- Payment page head: deadline sits in the meta line; no separate "Paying" line. Bar ends are rounded.
- Row hover on the overview: the status line cross-fades into a mini bar (sure / maybe / missing) that grows from the left. No page morph on click; a view just rises in.

## 10. Stable layout, rolling numbers (round 5)

- Payment page head: the three parts (Can rely on / Uncertain / Missing) are always three equal columns; an empty part shows "$0" muted. Reasons clamp to two lines with two lines reserved. The bar segments ease to new widths instead of being redrawn.
- Numbers that change while planning roll: the old value slides out and the new one slides in; up when the payment gets better, down when it gets worse (big head number, the three amounts, the plan result).
- Fixed heights: steps rows 60px (desktop), plan note line 16px. Measured during drags: head, result row, grid and list heights never change unless a step is added.
- A block too narrow for its text (own cash lands in 1–2 days) keeps the block at its true size and puts the label right beside it, on its own track, with a surface backing. The cash-needed-by line runs behind blocks and labels so no text is ever crossed.
- Ticking a step updates only that step and its block (no rebuild): the block locks with a check badge, its track fades, the lane line reads "✓ Requested". Done rows dim to 50% and glide to the end of the list; un-ticking brings them back in date order.

## 11. Bank balance line

- "Expected" means: money is counted at the start of the last day of its landing range (by then it is in), and a payment leaves in the middle of its due day. A day with both shows the rise first, then the drop, so an arrival is never hidden by a payment on the same day.
- Payment dots sit in the middle of their due day (point events are centered). Value labels are tried right of a change, then left of it, above then below; anything that would touch a label or a dot is dropped, the lowest point is placed first.
- Two different lines, two meanings. Payment page: the red dashed deadline sits right before the payment pin (start of its due day), labelled "Cash needed before Mon, Nov 9". Nothing lands on a weekend, so this equals "by the business day before". Overview hover: a thin neutral line through the payment's own dot marks the event; it is not a deadline and is never red.
- A narrow block first drops its date line, and only if the amount still doesn't fit puts the text beside it.
- The "n of m done" count rolls up/down when a step is ticked.
- Removing or resetting steps: the removed row fades where it was while the rows below glide up; the steps list stays fixed on screen (the page scrolls along when a lane above disappears) and the page never gets shorter under the reader. Both numbers in "n of m done" roll.
- The "Your cash" lane always exists. Empty, it holds the "+ Add your own cash" button at the default send window; adding fills the same lane, removing empties it. So nothing below (the payment lane, the steps list) ever moves when cash is added or removed. One cash entry per payment; its amount is typed in Your steps.
- Steps list motion is measured inside the list: if the whole list moves, its rows don't re-animate; only rows whose place in the list changes glide.
- "How these dates are worked out": states on the dots, durations on the lines between them. Colour moves one step at a time: open amber ring (delivered), open amber ring (released), filled amber (payout on its way), filled green (in your bank); the last line is solid and blends amber to green. Collapsing fades the text out first (120 ms) so nothing is clipped mid-sentence; opening fades it in after the panel starts.
- Fund fill follows the journey: filled amber = already on its way (payout sent); open amber outline = not sent yet (eligible, in reserve); grey hatch = on hold; filled green = in the bank. Same in the overview strip, the funds table swatches and the plan blocks. Dashed outlines are reserved for "where it was before your plan" and the empty cash slot.
