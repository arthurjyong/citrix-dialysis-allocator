# How it works

The whole tool is one HTML file with no server, no build step and no dependency. It runs offline, and it uses two browser features: the File System Access API to keep its work in a folder, and `DecompressionStream` to unpack PDF streams.

```
orders folder (PDFs)
      |
      v
Module 1, the reader:   PDF -> text runs -> lines -> boxes -> one record per order
      |
      v
Matching rules and built-in checks:   ticks the statuses, or stops the order with a reason code
      |
      +--> Need manual intervention: a nurse checks, then Accept or Delete
      |
      v
Unallocated, grouped by date:  Overdue, Today, later days
      |
      v
Module 2, the board:   allocation rules -> score per seat -> exact solver -> machines by sessions
      |
      v
Data folder:   state.json (the board), log.jsonl (the diary), copies/, storage/
```

## Module 1: the reader

The PDF parser is written from scratch in the page. It reads cross-reference tables and streams, and object streams, and it finds objects by scanning when the table is missing or wrong. It reads the fonts' character maps, and it follows the text operators of each page to get runs of text with their positions.

- Runs are sorted into lines by height on the page, then left to right, with spaces in proportion to the gap.
- Each box of the form is read by its label, and a box that is left out reads as empty.
- A file can hold several orders. A page with the form's title is an order of its own, and a page without one joins the order before it.
- A line that fits no box is kept where it falls, so no word is lost from the order text a nurse checks.

A file is copied into `storage/` under its Order ID with its SHA-256 checksum, and the original is removed only after the copy is checked. An order number the tool already holds is refused.

## Reason codes

Every stopped order carries a code and, where it helps, a quote from the order. A nurse sees why it stopped, not just that it did.

| Code | Meaning |
|---|---|
| R01 | Review new orders is on, so every new order waits for Accept |
| R02 | The usual centre matches none of the centre words |
| R03 | A matching rule sent the order for review |
| R10, R11 | The file is unreadable, or the page is not the order form |
| R12 to R17 | A required box is empty: order number, name, IC, location, date or priority |
| R18 | The form says there is no functioning vascular access |
| R19 | Another order with this IC is on the board for the same day |
| R21 | Another order for this patient is also overdue, so a nurse decides which one runs |

## Matching rules: who may use which machine

Each order has status ticks, such as MRSA, VRE, CP-CRE, C. diff, Isolation, Unknown and Hep B. Each machine has the same ticks, for what it takes. The rules that fill in a patient's ticks are sentences on the Settings page:

```
If [HP (if any)] has [any of] [MRSA]  tick [MRSA]
If [HepB case] has [any of] [Pending, Not Traced]  tick [Unknown]
If [HP (if any)] has [other than] [the known words]  triggers manual review
```

The machine's ticks are the single source of truth:

- A seat is green when the machine takes every status the patient carries. Auto slot uses green seats only.
- A seat is amber when it does not, and the mismatch is named. A nurse may still drop a patient there by hand.
- A seat is red when it crosses the hepatitis B line, in either direction. A nurse must confirm before it goes through.

## Allocation rules: who goes where

Every allocation rule is soft, and each is one sentence in one of four shapes:

```
Every order gets [100] when assigned to [the earliest slot possible]
A [Priority 1] order gets [200] when assigned to [the earliest slot possible]
Every order gets [20] for each day waited when assigned to [the earliest slot possible]
An order whose [Remarks and notes] has [any of] [await TDC, ...] gets [-1000] when assigned to [S1]
```

"The earliest slot possible" spreads a rule's points over the sessions at 100%, 50%, 33%, 25% and 20%. A rule that names one session gives all its points there. A patient's score for a seat is the sum of every rule that fires. Who is pushed to a later session depends on the drop in score between sessions, not on the height of the score.

All the numbers in the starting rules are placeholders, for the team using the tool to set.

## The solver

Auto slot takes the Overdue and Today orders, and every free green seat. Each rule concerns one patient in one seat, so the best board is a maximum-weight matching between patients and seats. That is solved exactly with the Hungarian method (Kuhn-Munkres), so no search or randomness is needed.

- Each weight goes in as a cost with a minus sign, and extra columns stand for "not placed".
- On equal totals, a small bonus puts an earlier order in an earlier seat.
- Seats are listed by session, then by the least special machine, so a special machine stays free when nothing else is at stake.
- The same board always gives the same answer.

Orders placed by hand stay where they are. Auto slot only fills empty seats, and it can run again at any time.

## The record of what happened

Every change makes one line in `log.jsonl`, and the whole board is saved to `state.json` a moment later. If the disk fails, the screen says so, nothing is lost and the save is tried again. Print and New day each write a copy to `copies/`. New day takes placed patients off the board and carries the rest over, sorted again by date.

## The sample orders

`tools/make_sample_orders.py` writes each order as a PDF, from a fixed seed and the day it is given. It reads no input file.
