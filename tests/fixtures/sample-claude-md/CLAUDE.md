# My App

A full-stack web application for task management.

## Stack

TypeScript / Next.js / Prisma / Tailwind CSS

## Commands

- `pnpm build` — build the project
- `pnpm test` — run tests
- `pnpm lint` — lint with ESLint
- `pnpm dev` — start dev server

## Architecture

- `src/app/` — Next.js App Router pages
- `src/components/` — React components
- `src/lib/` — shared utilities
- `src/server/` — API routes and server logic
- `prisma/` — database schema and migrations

## Conventions

- **Naming**: Use PascalCase for components, camelCase for utilities
- **Error Handling**: Always use try/catch with proper error logging
- **Imports**: Use absolute imports with @/ prefix
- **Components**: Prefer function components with TypeScript props

## Git

- Conventional commits: feat:, fix:, docs:, chore:
- Always rebase on main before PR
- PRs require at least one review

## Additional Notes

This project uses NextAuth for authentication.
Database is PostgreSQL via Prisma ORM.
