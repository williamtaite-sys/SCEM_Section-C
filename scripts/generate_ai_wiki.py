import os
import sys
import subprocess
from google import genai

# Configuration
# Ensure you set the GOOGLE_API_KEY environment variable
MODEL_NAME = "gemini-2.5-flash" 
SOURCE_DIR = "."
OUTPUT_DIR = "wiki_content"
FILES_TO_PROCESS = ["Section_C.ipynb"]

def git_pull():
    """Pulls the latest changes from the remote repository."""
    print("Pulling latest changes...")
    try:
        subprocess.run(["git", "pull"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error pulling changes: {e}")
        # We continue even if pull fails, as we might be working locally

def generate_docs_for_code(code_content, filename):
    """Uses Gemini to generate documentation for the code/notebook."""
    
    # Initialize the client with the API key from the environment
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    prompt = f"""
    You are a technical documentation expert. 
    
    Please write comprehensive documentation in Markdown format for the following Jupyter Notebook named '{filename}'.
    
    Since this is a Jupyter Notebook (likely containing data analysis or machine learning code), structure the documentation as follows:
    1. **Notebook Overview**: A high-level summary of the analysis or project contained in the notebook.
    2. **Key Findings/Objectives**: What is the notebook trying to achieve or prove?
    3. **Methodology**: Briefly describe the steps taken (e.g., Data Loading, Preprocessing, Model Training, Evaluation).
    4. **Key Code Components**: Highlight important functions, classes, or code blocks used.
       - Description
       - Purpose
    5. **Dependencies**: List key libraries used.
    
    Here is the content of the notebook (raw format):
    ```text
    {code_content[:100000]} 
    ```
    (Note: Content might be truncated if extremely large, prioritize the structure and visible code/markdown cells)
    """
    # Truncating to 100k chars to be safe, though Gemini 1.5/2.5 handles much more.
    
    # Call the API using the new SDK structure
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return clean_markdown_response(response.text)

def clean_markdown_response(text):
    """Removes markdown code fences if present."""
    if not text:
        return ""
    text = text.strip()
    if text.startswith("```markdown"):
        text = text[11:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]
    
    return text.strip()

def main():
    # 1. Update Repo
    git_pull()

    # 2. Check API Key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set.")
        sys.exit(1)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    combined_docs = ["# Project Documentation (AI Generated)\n\nWelcome to the AI-generated documentation.\n"]

    # 3. Process Files
    for fname in FILES_TO_PROCESS:
        if os.path.exists(fname):
            print(f"Generating AI docs for {fname}...")
            
            with open(fname, "r", encoding="utf-8") as f:
                code_content = f.read()
            
            try:
                md_content = generate_docs_for_code(code_content, fname)
                
                # Save individual page
                output_path = os.path.join(OUTPUT_DIR, f"{fname.replace('.ipynb', '')}.md")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                
                combined_docs.append(md_content)
                
            except Exception as e:
                print(f"Failed to generate docs for {fname}: {e}")
        else:
            print(f"File not found: {fname}")

    # 4. Create Home.md (Initial placeholder, organize_wiki.py will overwrite/refine)
    with open(os.path.join(OUTPUT_DIR, "Home.md"), "w", encoding="utf-8") as f:
        f.write("\n---\n".join(combined_docs))

    print(f"AI Documentation generated in {OUTPUT_DIR}/")
    print("To publish, run your git wiki publish commands or the GitHub Action.")

if __name__ == "__main__":
    main()
