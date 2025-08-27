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

## Example Output
Pull Request https://github.com/jeremyary/notebook-review-poc/pull/2
