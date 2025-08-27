# Notebook Review Action

GitHub Action that reviews Jupyter notebooks in PRs using an OpenAI-compatible model API.

## Setup

1. Add these secrets to your repository:
   - `RH_MODEL_API_KEY` - API key for the model
   - `RH_MODEL_URL` - Base URL for the API endpoint
   - `RH_MODEL_NAME` - Name of the model to use
2. Notebooks in PRs are automatically reviewed

## Local Testing

```bash
# 1) Install dependencies
pip install -r requirements.txt

# 2) Create .env file (copy from example)
cp .env.example .env

# 3) Edit .env with your actual values

# 4) Run review
python scripts/review_notebooks.py changed_notebooks.txt
```

Alternative without .env file:
```bash
export RH_MODEL_API_KEY="your-api-key"
export RH_MODEL_URL="https://your-api-endpoint.com"
export RH_MODEL_NAME="your-model-name"
python scripts/review_notebooks.py changed_notebooks.txt
```

## What it Reviews

- Clear Header
- Goal/Objective Present
- Setup & Pre-Requisites
- Markdown Usage
- Avoid Hardcoding
- Inline Code Comments
- Next Steps & Conclusion

Results show as: ✅ Good | ⚠️ Warning | ❌ Problem | 💡 Suggestion

## Exit Codes

- **0**: All notebooks passed review (no problems found)
- **1**: One or more notebooks have problems (❌ status)

In GitHub Actions, the workflow will fail if any notebook has a "problem" status.