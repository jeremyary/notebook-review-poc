# Notebook Review Action

GitHub Action that reviews Jupyter notebooks in PRs using Claude AI

## Setup

1. Add `ANTHROPIC_API_KEY` to repository secrets
2. Notebooks in PRs are automatically reviewed

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run review
export ANTHROPIC_API_KEY="your-api-key"
python scripts/review_notebooks.py changed_files.txt
```
