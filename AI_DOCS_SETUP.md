# AI Documentation Kit (`.ai-docs`) - Deployment Guide

This guide explains how to add automated, AI-driven documentation generation to any GitHub repository. The system uses Google's Gemini models to analyze your code and notebooks, generating a structured GitHub Wiki that updates automatically on every push.

## 📦 What's in the Kit?

The kit consists of two main components:
1.  **`.ai-docs/`**: A self-contained directory holding the configuration, templates, and scripts.
2.  **`.github/workflows/update_wiki.yml`**: A GitHub Action that triggers the process.

## 🚀 Deployment Instructions

To enable auto-documentation for your repository, follow these steps:

### 1. Copy Files
Copy the following files/folders from the source template (e.g., `SCEM_Section-C`) into the root of your target repository:

*   Copy the entire `.ai-docs/` folder.
*   Copy `.github/workflows/update_wiki.yml`.

Your repo structure should look like this:
```text
My-Repo/
├── .ai-docs/
│   ├── config.yaml
│   ├── requirements.txt
│   ├── scripts/
│   └── templates/
├── .github/
│   └── workflows/
│       └── update_wiki.yml
└── src/ (or your code)
```

### 2. Configure `config.yaml`
Open `.ai-docs/config.yaml` and customize it for your project:

*   **`project_name`**: Set the title of your documentation.
*   **`targets`**: Define which files to document. You can have multiple groups with different templates.
    ```yaml
    targets:
      - name: "Jupyter Notebooks"
        pattern: "**/*.ipynb"       # Finds all notebooks
        template: "data_science.md" # Uses the data science prompt
        category: "Analysis"        # Groups them under "Analysis" in the sidebar

      - name: "ETL Scripts"
        pattern: "etl/**/*.py"
        template: "generic.md"
        category: "Data Pipelines"
    ```
*   **`ignore_patterns`**: Add any file paths you want to exclude (e.g., `**/tests/**`).

### 3. Customize Prompts (Optional)
Look in `.ai-docs/templates/`. You will see markdown files like `data_science.md`.
*   These are the instructions sent to the AI.
*   You can edit them to change the output style, add specific sections (e.g., "List all SQL tables referenced"), or enforce formatting rules.

### 4. Set GitHub Secrets
The system requires a Google API Key to access the Gemini model.

1.  Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**.
2.  Click **New repository secret**.
3.  Name: `GOOGLE_API_KEY`
4.  Value: [Your Google Gemini API Key]

### 5. Enable Wiki Write Access
The GitHub Action needs permission to write to the Wiki.
1.  Go to **Settings** -> **Actions** -> **General**.
2.  Scroll to **Workflow permissions**.
3.  Select **Read and write permissions**.
4.  Click **Save**.

### 6. Push & Run
Commit the files and push to your `main` or `master` branch.
```bash
git add .ai-docs .github
git commit -m "Setup: Add AI Documentation Kit"
git push origin main
```
The Action will start automatically. You can view progress in the **Actions** tab. Once finished, click the **Wiki** tab to see your new documentation!

---

## 🔧 Maintenance

*   **Changing the Model**: Edit `config.yaml` to change `model` (e.g., from `gemini-2.0-flash-exp` to `gemini-1.5-pro`).
*   **Adding New File Types**: Simply add a new entry to the `targets` list in `config.yaml` and optionally create a new template in `templates/`.
