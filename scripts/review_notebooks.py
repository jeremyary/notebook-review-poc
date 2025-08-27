#!/usr/bin/env python3
"""
Notebook Review Script
Performs Claude-based review of Jupyter notebooks in Pull Requests

File authored using AI for reference and/or assistance.
"""

import sys
import os
import json
from pathlib import Path
from typing import List
import logging
import nbformat
from openai import OpenAI
from tabulate import tabulate
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_notebook(filepath: Path) -> nbformat.NotebookNode:
    """Load a Jupyter notebook file using nbformat."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    notebook_data = nbformat.reads(content, as_version=4)
    return notebook_data


def extract_notebook_text(notebook_data: nbformat.NotebookNode) -> str:
    """Extract all text content from notebook cells."""
    cells = []
    for cell in notebook_data.cells:
        if cell.cell_type == "markdown":
            cells.append(cell.source)
        elif cell.cell_type == "code":
            cells.append(f"# Code:\n{cell.source}")
    return "\n\n".join(cells)


def review_notebook(notebook_data: nbformat.NotebookNode, filepath: Path) -> str:
    """Perform model-based review of the notebook."""
    # Get configuration from environment
    api_key = os.getenv('RH_MODEL_API_KEY')
    base_url = os.getenv('RH_MODEL_URL')
    model_name = os.getenv('RH_MODEL_NAME')
    
    if not api_key:
        raise ValueError("RH_MODEL_API_KEY environment variable not set")
    if not base_url:
        raise ValueError("RH_MODEL_URL environment variable not set")
    if not model_name:
        raise ValueError("RH_MODEL_NAME environment variable not set")
    
    # Extract notebook text
    notebook_text = extract_notebook_text(notebook_data)
    
    # Prepare prompt
    review_prompt = f"""
Here is a Jupyter notebook for review:

{notebook_text}

Review this notebook against these guidelines and return your assessment as JSON:
- Clear Header: Does the notebook have a clear title/header?
- Goal/Objective Present: Is the purpose clearly stated?
- Setup & Pre-Requisites: Are requirements and setup steps documented?
- Markdown Usage: Are markdown cells used effectively for explanations?
- Avoid Hardcoding: Are values parameterized rather than hardcoded?
- Inline Code Comments: Is the code well-commented?
- Next Steps & Conclusion: Does it end with conclusions or next steps?

For each guideline, provide:
- status: one of "good", "warning", "problem", or "suggestion"
- message: a brief, actionable suggestion (or "Looks good" if no issues)

Return ONLY valid JSON in this exact format. Do not, under any circumstance, wrap the json in a json code display block:
{{
  "guidelines": [
    {{"name": "Clear Header", "status": "good", "message": "Looks good"}},
    {{"name": "Goal/Objective Present", "status": "warning", "message": "Add a brief overview of the analysis goals"}},
    // ... continue for all guidelines
  ]
}}
"""
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model_name,
        max_tokens=1000,
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are a helpful reviewer of Jupyter Notebooks."},
            {"role": "user", "content": review_prompt}
        ]
    )
    
    return response.choices[0].message.content


def format_review_as_ascii_table(json_result: str) -> str:
    """Format JSON review result as an ASCII table."""
    try:
        data = json.loads(json_result)
        
        # Define status emojis
        status_icons = {
            "good": "✅ Good",
            "warning": "⚠️ Warning", 
            "problem": "❌ Problem",
            "suggestion": "💡 Suggestion"
        }
        
        # Extract guidelines from JSON and format them
        guidelines = data.get("guidelines", [])
        table_data = []
        
        for guideline in guidelines:
            name = guideline.get('name', '')
            status_icon = status_icons.get(guideline.get('status', ''), '❓')
            message = guideline.get('message', '')
            table_data.append([name, status_icon, message])
        
        # Create table headers
        headers = ['Guideline', 'Status', 'Suggestion']
        
        markdown_table = tabulate(
            table_data,
            headers=headers,
            tablefmt='github',
            colalign=('left', 'left', 'left')
        )
        
        ascii_table = tabulate(
            table_data,
            headers=headers,
            tablefmt='simple',
            colalign=('left', 'left', 'left')
        )
        
        # Write to GitHub summary
        summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
        if summary_file:
            with open(summary_file, 'a') as f:
                f.write("## 📋 Notebook Guidelines Report\n\n")
                f.write(markdown_table)
                f.write("\n\n")
        
        return ascii_table

    except json.JSONDecodeError:
        # if parsing fails, return the JSON payload
        return json_result


def process_notebooks(notebook_files: List[Path]) -> bool:
    """Process and review a list of notebook files.
    
    Returns:
        True if any problems were found, False otherwise
    """
    has_problems = False
    
    for notebook_file in notebook_files:
        try:
            notebook_data = load_notebook(notebook_file)
            
            result = review_notebook(notebook_data, notebook_file)
            print(f"\n## Review of {notebook_file}\n")
            
            # Check for problems in the JSON result
            try:
                data = json.loads(result)
                guidelines = data.get("guidelines", [])
                file_has_problems = any(g.get("status") == "problem" for g in guidelines)
                if file_has_problems:
                    has_problems = True
                    print("⚠️  Problems found in this notebook\n")
            except json.JSONDecodeError:
                # If we can't parse JSON, assume there's a problem
                has_problems = True
            
            # Try to format as ASCII table, fall back to raw output if needed
            formatted_result = format_review_as_ascii_table(result)
            print(formatted_result)
            
        except Exception as e:
            logger.error(f"Failed to process {notebook_file}: {e}")
            print(f"\n❌ Error processing {notebook_file}: {e}")
            has_problems = True
    
    return has_problems


def main():
    """Main entry point"""
    # Load .env file if it exists (for local development)
    load_dotenv()
    
    if len(sys.argv) != 2:
        print("Usage: python review_notebooks.py <changed_files.txt>")
        sys.exit(1)
    
    changed_files_path = Path(sys.argv[1])
    
    # Read the list of changed files
    notebook_files = []
    
    try:
        with open(changed_files_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and line.endswith('.ipynb'):
                    notebook_files.append(Path(line))
    except FileNotFoundError:
        logger.info("No changed notebook files found")
        print("No notebook files changed in this PR")
        sys.exit(0)
    
    # Check if required environment variables are available
    missing_vars = []
    for var in ['RH_MODEL_API_KEY', 'RH_MODEL_URL', 'RH_MODEL_NAME']:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print(f"❌ Error: The following environment variables are required: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Process the notebooks
    has_problems = process_notebooks(notebook_files)
    
    # Exit with appropriate code
    if has_problems:
        print("\n❌ Review failed, problems found in one or more notebooks")
        sys.exit(1)
    else:
        print("\n✅ Review passed, all notebooks look good")
        sys.exit(0)


if __name__ == "__main__":
    main()