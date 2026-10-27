# Search Queries for Job Scraper

Profile focus: **remote / freelance CAD and civil-engineering design projects** (civil engineer, Brazil). Not a traditional full-time job search.

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first (`linkedin-search`, `freehire-search`). The Danish portals ship disabled and stay disabled (Brazil market).

The `site:` queries below are the **WebSearch fallback** and the main route for freelance platforms, which have no CLI skill yet.

**Language scope:** write queries in Portuguese and English. English opens the international remote market; Portuguese covers Brazilian platforms. (English proficiency level is not yet confirmed in CLAUDE.md; a posting that requires fluent English is flagged for the candidate's judgment, per `04-job-evaluation.md`.)

## Search Sites

Freelance / project platforms (primary):
- **workana.com** - Latin American freelance marketplace (Portuguese/Spanish)
- **99freelas.com.br** - Brazilian freelance marketplace
- **upwork.com** - international, remote, English
- **freelancer.com** - international, remote, English
- **fiverr.com** - gig marketplace (offers, not job posts; useful for pricing benchmarks)

Secondary:
- **linkedin.com/jobs** - filter: contract / remote / Brazil or worldwide; also covered by `linkedin-search`
- Direct Google searches for engineering/drafting firms that outsource CAD work

## Query Categories

Organized by function, not exact title.

### Priority 1: CAD drafting and design (AutoCAD)

Strongest match: AutoCAD is the candidate's primary design tool.

```
site:workana.com AutoCAD projetista remoto
site:workana.com desenho CAD projeto
site:99freelas.com.br AutoCAD projetista
site:99freelas.com.br desenhista CAD
site:upwork.com "AutoCAD" drafting remote
site:upwork.com "2D drafting" civil
site:freelancer.com AutoCAD drawing civil
site:linkedin.com/jobs "AutoCAD" freelance remote
```

### Priority 2: Roads, geometric design, signage, urban mobility

Matches documented experience: geometric road design, vertical/horizontal signage, public lighting, urban mobility studies.

```
site:workana.com projeto geométrico rodoviário
site:workana.com sinalização viária projeto
site:99freelas.com.br projeto viário engenheiro civil
site:upwork.com "road design" civil engineer remote
site:upwork.com "geometric design" highway AutoCAD
site:freelancer.com civil 3D road design
```

### Priority 3: Structures, foundations, buildings

Matches: reinforced-concrete and steel structural calculation, shallow/deep foundations, renovations.

```
site:workana.com projeto estrutural concreto armado
site:workana.com projeto de fundação engenheiro civil
site:99freelas.com.br projeto estrutural
site:upwork.com "structural drafting" concrete steel remote
site:freelancer.com structural engineering drawings AutoCAD
```

### Priority 4: Geotechnics, pavement, reports and permits

Matches: geotechnical reports and studies, asphalt pavement specialization, ARTs.

```
site:workana.com laudo geotécnico engenheiro
site:99freelas.com.br geotecnia pavimentação projeto
site:upwork.com geotechnical engineer remote report
site:upwork.com "pavement design" civil remote
```

### Priority 5: Planning and project management (secondary)

Matches: project management, scheduling in MS Project, management reports.

```
site:workana.com planejamento de obras MS Project
site:99freelas.com.br planejamento e controle de obras
site:upwork.com "MS Project" construction planning remote
```

## Location Filter

Remote work is required; physical location is not a constraint.
- Accept: remote anywhere, remote Brazil, remote Latin America
- Prefer: payment in a method the candidate can receive in Brazil (BRL, USD via platform)
- Exclude: on-site only, or "must reside in <country>" requirements that exclude Brazil

## Language Filter

Postings in Portuguese: fine. Postings in English: include, and flag if the project requires fluent client communication (English level not yet declared). Exclude postings requiring a language the candidate has not declared at all, per the Language Gate in `04-job-evaluation.md`.

## Project Filter (replaces Date Filter for freelance)

Prefer postings that are recent (last 14 days; freelance postings go stale within days). For each result record: platform, scope, estimated budget or hourly rate, deadline, client history/rating when shown, and whether the brief includes drawings or only a verbal description. Flag postings with no budget, clearly below-market prices, or requests to work for free ("test drawing") as low priority.

## Adapting Queries

If the user specifies a focus area (for example "/scrape structural" or "/scrape road"), select queries from the matching category and also generate 2-3 custom queries for that focus.
