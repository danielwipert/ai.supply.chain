"""Pipeline settings. Model choices are logged in docs/decisions.md."""

# Spec 6.4: cheap model drafts, top-tier model from a different family verifies.
DRAFT_MODEL = "deepseek/deepseek-v4.1-flash"
VERIFY_MODEL = "openai/gpt-6.1-sol"
