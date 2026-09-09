"""Muse — Your Creative Growth Companion — internal package.

Modules
-------
theme    : design-system CSS injection.
ai       : Gemini client + AI helpers + creator profile/context (business logic).
features : feature/AI generation functions + markdown formatters (business logic).
ui       : reusable presentation components and navigation helpers (UI only).
pages    : page renderers, sidebar, and router (UI only).

Business logic in `ai` and `features` is intentionally kept untouched; only the
presentation layer (theme/ui/pages) composes it into a SaaS-style dashboard.
"""
