# archaeocode

Excavate the ancient history buried in any git repository.

`archaeocode` surfaces patterns in git history that standard tools don't show you — which files haven't been touched in years, which files change constantly, and exactly how old every line of code really is.

## Install

```bash
git clone https://github.com/JipSanders/archaeocode
cd archaeocode
pip install -e .
```

**Requirements:** Python 3.10+, git

## Commands

### `survey` — Age profile of the whole repository

Get an instant read on whether you're working with a fresh codebase or inherited archaeology.

```
archaeocode survey --path /path/to/repo
```

```
╭─────────────────────────────── Repository Survey ───────────────────────────────╮
│ /path/to/myproject                                            214 tracked files  │
╰─────────────────────────────────────────────────────────────────────────────────╯
  < 1 week       ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░      18 files    8.4%
  < 1 month      ██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░      74 files   34.6%
  < 3 months     ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░      62 files   29.0%
  < 6 months     ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░      21 files    9.8%
  < 1 year       ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░      15 files    7.0%
  1 – 2 years    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░      14 files    6.5%
  2 + years      ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░      10 files    4.7%

  Oldest:  src/legacy/parser.py  (3y 2mo ago)
  Newest:  src/api/routes.py  (2d ago)
  Median:  2mo ago
```

---

### `churn` — Find the most volatile files

High churn means a file changes constantly — a hotspot, contested terrain, or code that never quite got right. Low churn means stable, trusted bedrock. `git` can't tell you this without scripting.

```
archaeocode churn --path /path/to/repo
```

```
  Commits                              File                              Authors
──────────────────────────────────────────────────────────────────────────────────
       87   ████████████████████████   src/api/routes.py                       4
       54   ████████████████░░░░░░░░   src/components/Dashboard.tsx            3
       41   ████████████░░░░░░░░░░░░   src/lib/auth.ts                         2
       29   █████████░░░░░░░░░░░░░░░   package.json                            4
        4   █░░░░░░░░░░░░░░░░░░░░░░░   src/lib/db.ts                           1
        2   ░░░░░░░░░░░░░░░░░░░░░░░░   src/legacy/parser.py                    1
```

`routes.py` touched 87 times, `parser.py` twice — immediately tells you where the instability lives.

---

### `dig` — Find the oldest, untouched files

Find what's been quietly sitting there since the early days. Good for spotting dead code, forgotten utilities, or APIs nobody remembers writing.

```
archaeocode dig --path /path/to/repo -n 10
```

```
     Age                        File                    Last Commit              Date
────────────────────────────────────────────────────────────────────────────────────────
      3y   ██████████████████   src/legacy/parser.py    Initial implementation   2022-01-04
      2y   ██████████████░░░░   src/utils/format.py     Add currency helpers     2023-03-12
      1y   █████████░░░░░░░░░   src/config/defaults.py  Set prod timeouts        2024-02-28
     6mo   ██████░░░░░░░░░░░░   src/lib/email.ts        Fix reply-to header      2024-10-31
```

---

### `excavate` — A file's commit history, layer by layer

The diff bars make it instantly obvious which commits were major rewrites vs minor fixes.

```
archaeocode excavate src/api/routes.py --path /path/to/repo
```

```
╭──────────────────────────── Excavation Report ─────────────────────────────╮
│ src/api/routes.py                                              87 commits   │
╰────────────────────────────────────────────────────────────────────────────╯
  ◆ f3a9c12e  fix: rate limit header on /api/auth
    2025-04-29 09:14  alice  4d  ░░░░░░░░░░░░░░░░░░░░░░░░  +2 -1
    │
  ◇ 9b2e8a01  feat: add /api/export endpoint
    2025-04-21 16:32  bob    2w  ████░░░░░░░░░░░░░░░░░░░░  +84 -12
    │
  ◇ 3d7f1c44  refactor: split auth and resource routes
    2025-03-15 11:08  alice  7w  ████████████████████████  +312 -287
```

---

### `carbon-date` — How old is each line of code?

Every line colored by the age of the commit that last touched it — green for recent, red for ancient. Instantly reveals which parts of a file are legacy and which are fresh.

```
archaeocode carbon-date src/lib/auth.ts --path /path/to/repo
```

```
╭──────────────────────────────── Carbon Dating ────────────────────────────╮
│ src/lib/auth.ts                                               94 lines     │
╰───────────────────────────────────────────────────────────────────────────╯
  Age key: █ <1mo  █ <3mo  █ <6mo  █ <1yr  █ <2yr  █ 2yr+

   1 f3a9c12e   4d  alice         │ import { SignJWT, jwtVerify } from 'jose';
   2                              │ import { cookies } from 'next/headers';
   3 9a1b3f02   2y  bob           │ const SESSION_DURATION = 60 * 60 * 24 * 7;
   4 f3a9c12e   4d  alice         │
   5                              │ export async function createSession(userId) {

──────────────────────────────── Age Distribution ──────────────────────────
  < 1 month      ████████░░░░░░░░░░░░░░░░░░░░░░░░      18 lines   19.1%
  < 3 months     ████████████░░░░░░░░░░░░░░░░░░░░      28 lines   29.8%
  1 – 2 years    ████████████████████░░░░░░░░░░░░      48 lines   51.1%
```

---

## Testing against any public repository

```bash
git clone https://github.com/pallets/flask /tmp/flask
archaeocode survey --path /tmp/flask
archaeocode churn --path /tmp/flask
archaeocode dig --path /tmp/flask
archaeocode carbon-date src/flask/app.py --path /tmp/flask
```

Or from inside a repo:

```bash
cd /path/to/repo
archaeocode survey
archaeocode churn -n 10
```

## Why

`git log` and `git blame` tell you *what* changed. `archaeocode` tells you *what the pattern of changes means*:

- **Which files should I be nervous about touching?** → `churn`
- **Is this repo actively maintained or frozen in time?** → `survey`
- **What code has nobody looked at in years?** → `dig`
- **Is this function ancient or was it just written last month?** → `carbon-date`

---

MIT License
