# Creating Shareable Guides from Wiki/Vault Conventions

When the user asks for a guide they can share (give to others, drop into agents, publish), synthesize from existing skills and vault state into a self-contained document.

## When to Use

- "Create a guide I can share with anyone"
- "Make this so someone else's agent can replicate it"
- "Document how we do X so I can give it to people"

## Process

### 1. Gather from Multiple Sources

The guide draws from several skills and live state. Load all relevant skills first:

- **Primary skill** (e.g., `llm-wiki` for wiki workflows, `obsidian` for vault ops)
- **Supporting skills** (e.g., `memory-curator` for curation pipeline)
- **References** (e.g., `wiki-ecosystem-architecture.md` for pipeline overview)
- **Live state** (e.g., vault directory structure, agent SOUL.md files)

### 2. Strip Personal Information (CRITICAL)

Before delegating or writing, audit for personal data. Common leaks:

| Category | Examples | Replacement |
|----------|----------|-------------|
| **User paths** | `/Users/username/...` | `~/vault` or `/path/to/...` |
| **Usernames** | GitHub handles, Discord IDs | Omit or use placeholders |
| **Channel names** | `#channel-name`, chat IDs | Omit entirely |
| **Vault names** | `"My Vault"`, `"Hermes Vault"` | Use generic `vault/` |
| **Agent names** | Specific profile names | Use role names (`knowledge-agent`) |
| **API keys** | Tokens, credentials | Omit entirely |
| **Dates** | Specific session dates | Use `YYYY-MM-DD` templates |

### 3. Structure for Agent Consumption

The guide must be **droppable** — an agent reading it cold can execute the workflows. This means:

- **Numbered steps** with exact commands (not "do X somehow")
- **Templates** that can be copied verbatim (SCHEMA.md, frontmatter, prompts)
- **Decision trees** for when-to-do-what (not just how)
- **Pitfalls section** — the silent failures that degrade the system over time
- **Quick start checklist** — from zero to running in numbered steps
- **Skills list** — what to install, with install commands

### 4. Verify No Leaks

After writing, search the output for personal identifiers:

```bash
# Search for common leak patterns
search_files pattern="username|/Users/|discord|channel-id" path="<output-file>"
```

Zero results = clean.

### 5. Self-Containment Test

The guide passes the test if an agent with no prior context can:
1. Set up the directory structure from the checklist
2. Copy templates verbatim
3. Run workflows from the step-by-step instructions
4. Avoid pitfalls from the gotchas section
5. Install required skills from the provided list

## Guide Template Structure

```
# [System] × [Tool]: [Subtitle]

> One-line description + self-containment statement

## Table of Contents

## Overview
- What the system does
- Architecture diagram (ASCII)
- Key principle (single-writer, approval-gated, etc.)

## [Layer/Component 1]
- What it is, who writes, what it handles

## [Layer/Component 2]
...

## Vault/Directory Structure
- Full tree with annotations

## [Configuration Template]
- Copy-pasteable config with placeholders

## The [Agent Role]
- Identity block (SOUL.md style)
- Responsibilities: Owns / Creates / Monitors / Reports / Never
- Agent prompt template

## Core Workflows
- Numbered step-by-step for each workflow
- Real commands, real templates

## Environment Variables
- Table of required vars

## Cron Jobs
- YAML configs for recommended schedules

## Pitfalls & Gotchas
- Categorized by type (immutability, discipline, detection)

## Quick Start Checklist
- Numbered from zero to running

## Skills to Install
- Table + install commands

## Appendices
- File templates, format conventions, tool recommendations
```

## Delegation Pattern

For large guides (500+ lines), delegate to a subagent with:
- All gathered context (skill contents, reference docs, vault state)
- Explicit personal-info stripping instructions
- Target line count (800-1200 for comprehensive guides)
- Output path on the Desktop (easy to find and share)

Verify the output with `search_files` for leaks before reporting to the user.
