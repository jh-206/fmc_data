# AGENTS.md

## Scope

This project contains code, data-related workflows, and documentation.
You may read and modify project files as needed, but prefer minimal, targeted changes.

Current active top-level working directories are:
- `src/` for source code
- `data/` for active project data
- `docs/` for project documentation

Within `docs/`:
- `docs/notes.md` is a running working log for verbose notes, attempted approaches, failures, open questions, and follow-up items.
- Ask for confirmation before making substantive updates to `docs/notes.md`, but the confirmation threshold can be lighter when the user has clearly asked to record current work.
- `docs/decisions.md` is the canonical record of project decisions, such as data labeling standards and official workflows.
- Ask for strict, explicit confirmation before adding to or changing `docs/decisions.md`.

The `archived/` directory contains legacy or historical materials kept for reference.
Do not modify, reorganize, or delete anything under `archived/` unless the user very clearly and explicitly directs you to do so.

## Core Rules

- Do not fabricate results, behavior, or facts about the project.
- Preserve the intent of existing code and writing unless explicitly asked to change it.
- Prefer small, localized edits over broad rewrites.
- Do not change meanings, assumptions, or interfaces without a clear reason.
- When uncertain, leave things unchanged and surface the uncertainty.

## Editing Guidelines

- Improve clarity, correctness, and maintainability.
- Keep existing structure, terminology, and style when reasonable.
- Avoid unnecessary renaming, reformatting, or churn.
- Make changes that are easy to review.
- When rewriting text, present clean replacement text rather than partial fragments.

## User Pacing

- If the user asks to acknowledge, restate, or repeat the goal before proceeding, do only that.
- Do not start research, edits, downloads, or other substantive work until the user confirms.

## Secrets And Tokens

- Treat API tokens, credentials, and secret config files as sensitive.
- Never print, quote, summarize, or copy secret values into chat, logs, commits, docs, or generated files.
- Never commit real tokens or credentials. Only create or edit template files with placeholder values unless the user explicitly asks otherwise.
- Prefer local untracked files such as `etc/tokens.json` for secrets, and tracked `*.initial` files for placeholders.
- Do not open, read, or use a secrets file unless the task requires it and the user has clearly asked for that step.
- Before using a token in a network request or external tool call, briefly state that this is the step requiring the secret and wait for confirmation.
- If a secret may have been exposed, stop and tell the user to rotate or revoke it.

## Disallowed Actions

- Do not invent missing project context.
- Do not make large destructive changes without explicit instruction.
- Do not silently remove important content, logic, or constraints.
