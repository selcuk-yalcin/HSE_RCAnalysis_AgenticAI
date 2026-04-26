# Specs Directory

This folder contains the project's spec-driven development artifacts.

## Purpose

- Keep planning and implementation aligned.
- Make scope changes explicit before code changes.
- Provide a stable source of truth for AI-assisted development in Cursor.

## Files

- `plan.md`: Product and architecture baseline derived from the current project state.
- `roadmap.md`: Prioritized execution backlog derived from `TODO.md`.
- `tech-stack.md`: Runtime, infrastructure, and component technology map.

## Workflow

1. Update relevant spec file first (`plan.md` or `roadmap.md`) for any non-trivial change.
2. Implement code changes.
3. Update the spec if implementation decisions changed.
4. Keep `README.md` and `specs/` in sync.

## Spec-Driven Levels in This Project

- **spec-first** for large features and architecture changes.
- **spec-anchored** for medium changes with clear existing scope.
- **spec-as-source** for bug fixes and constrained maintenance.
