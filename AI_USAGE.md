# AI Usage Disclosure

## Summary

**Cursor and AI-assisted tooling were used to accelerate development** of this assessment submission. The author remained responsible for requirements interpretation, architectural choices, test validation, and final code review.

## How AI was used

- **Planning:** breaking the work into incremental commits (structure → tests → implementation → API → seed → frontend → docs)
- **Test ideas:** suggesting edge cases for validation, pagination, insights with zero employees, and API error paths
- **Scaffolding:** initial project layout, boilerplate for FastAPI layers, React components, and fetch-based API client
- **Refactoring suggestions:** e.g. moving table creation out of route handlers, using SQL aggregates for insights, batching seed inserts
- **Documentation:** drafts for README, design notes, tradeoffs, and demo script (reviewed and aligned to the actual codebase)

## How correctness was validated

- **pytest** suite run repeatedly during backend work (currently 59 tests)
- **Manual reasoning** about layer boundaries (API vs service vs repository)
- **Frontend production build** (`npm run build`) for TypeScript correctness
- **Local manual testing** of employee CRUD, filters, pagination, and insights tabs against a seeded database

## What was not done

- No blind copy-paste of large unrelated code blocks without reading and adapting them
- No reliance on AI-generated commits as git author (commits attributed to the human author)
- No substitution of tests with “it should work” assumptions — failing tests were fixed before moving on

## Design intent

Complexity was deliberately kept low: modular monolith, SQLite, simple React state, no microservices, no auth framework, no chart library. AI suggestions that increased scope without assessment value were declined or simplified.
