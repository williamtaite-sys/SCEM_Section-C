# AI Documentation Kit (`.ai-docs`) - Deployment Guide

This guide explains how to add automated, AI-driven documentation generation to any GitHub repository. The system uses Google's Gemini models to analyze your code and notebooks, generating a structured GitHub Wiki that updates automatically on every push.

## 📦 What's in the Kit?

The kit consists of two main components:
1.  **`.ai-docs/`**: A self-contained directory holding the configuration, templates, and scripts (including the `discover_targets.py` script which automatically maps your project files to documentation templates).
2.  **`.github/workflows/update_wiki.yml`**: A GitHub Action that triggers the discovery and generation process.

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
│   │   ├── discover_targets.py
│   │   ├── generate_docs.py
│   │   └── organize_docs.py
│   └── templates/
├── .github/
│   └── workflows/
│       └── update_wiki.yml
└── src/ (or your code)
```

### 2. Configure `config.yaml`
Open `.ai-docs/config.yaml` and customize it. The system is designed to be "Zero Config" for common file types.

*   **Global Settings**:
    - `project_name`: The title of your documentation.
    - `templates_dir`: Where your prompts are stored (default: `.ai-docs/templates`).
*   **Auto-Discovery (Recommended)**:
    The `auto_discovery` section defines rules. If the system finds these file types in your repo, it will automatically create documentation for them using the specified template.
    ```yaml
    auto_discovery:
      ".sql":
        template: "sql.md"
        category: "Database"
        target_name: "SQL Scripts"
    ```
*   **Manual Targets**:
    If you need to document a specific folder or file with a unique template, add it to `targets`. Manual targets always take precedence.

### 3. Customize Prompts (Optional)
Look in `.ai-docs/templates/`. You will see markdown files like `data_science.md` or `matillion_orch.md`.
*   These are the instructions sent to the AI.
*   You can edit them to change the output style or add specific logic (e.g., "Always list security considerations").

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
git commit -m "Setup: Add AI Documentation Kit with Auto-Discovery"
git push origin main
```
The Action will start automatically. It will **discover** your files, **generate** documentation via AI, and **publish** it to your Wiki!

---

## 🔧 Maintenance

*   **Adding New File Types**: Simply add a new extension and template mapping to the `auto_discovery` section in `config.yaml`.
*   **Updating Logic**: Edit the markdown files in `templates/` to refine how the AI documents your code.
*   **Changing the Model**: Update the `model` field in `config.yaml` (e.g., `gemini-2.0-flash`).