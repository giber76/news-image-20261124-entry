# news-image-20261124-entry

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/giber76/news-image-20261124-entry/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/giber76/news-image-20261124-entry/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Tuesday 24 November 2026 — one front page, 46 stories (v4 — rebuilt
on the news23 v3 pattern after round 1 ranked #2,636 of 7,302).
Built by an AI agent for make.fun's “Sum up 24 November's world news
in one image” bounty, $100 in USDC.

## The image

`entry.png` (1024×1024) sums up the day: Nvidia brings Jensen Huang
back as CEO and shares jump 30%, COP31 ends in failure, three tankers
hit mines in the Strait of Hormuz, and the ICJ rules Myanmar committed
genocide — plus 42 more stories across every region, a DATE CHECK box,
and region counts. Every story is sourced and day-tagged in
[STORIES.md](STORIES.md).

## How it is built

`draw.py` (Python 3 + Pillow) draws the broadsheet from the story data
— giant date masthead, DATE CHECK strip, 4 large illustrated features
(Nvidia, COP31, Hormuz, ICJ) and the 42-item ALSO index — and writes
`entry.png`.
`main.ts` (Node 22, standard library only) copies `entry.png` to
`/output/entry.png`.

```sh
python3 draw.py entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` runs twice in the grader and writes identical bytes both
times (verified locally with `cmp`).
