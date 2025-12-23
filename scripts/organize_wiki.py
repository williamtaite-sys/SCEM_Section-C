import os
import glob
from google import genai

# Configuration
MODEL_NAME = "gemini-2.5-flash"
OUTPUT_DIR = "wiki_content"

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

def read_markdown_files():
    """Reads all module documentation files."""
    docs = {}
    # We look for all .md files except Home.md and _Sidebar.md to avoid reading old versions
    files = glob.glob(os.path.join(OUTPUT_DIR, "*.md"))
    for fpath in files:
        fname = os.path.basename(fpath)
        if fname not in ["Home.md", "_Sidebar.md"]:
            with open(fpath, "r", encoding="utf-8") as f:
                docs[fname] = f.read()
    return docs

def generate_home_page(client, docs):
    """Generates a cohesive Home.md."""
    print("Generating Home.md...")
    
    docs_context = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in docs.items()])
    
    prompt = f"""
    You are a Lead Technical Writer. You are organizing the Wiki for a data science/software project.
    
    Here is the documentation for the components in the project:
    {docs_context}
    
    Your task:
    Write a new 'Home.md' file.
    1. It must provide a high-level system/analysis overview.
    2. It must explain the key analyses or models present.
    3. It must link to the individual pages using the format `[[Page Name|Filename_without_extension]]`.
       Example: If the file is `Section_C.md`, link to it as `[[Section C Analysis|Section_C]]`.
    4. Keep it professional, welcoming, and clear.
    """
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return clean_markdown_response(response.text)

def generate_sidebar(client, docs):
    """Generates a _Sidebar.md for navigation."""
    print("Generating _Sidebar.md...")
    
    docs_list = list(docs.keys())
    
    prompt = f"""
    You are a Lead Technical Writer.
    
    Here is the list of markdown files in our Wiki:
    {docs_list}
    
    Your task:
    Create the content for a GitHub Wiki `_Sidebar.md` file.
    1. Group related items logically (e.g., "Analysis Notebooks", "Data Scripts").
    2. Use the standard GitHub Wiki link format: `[[Link Label|Filename_without_extension]]`.
    3. Start with a link to `[[Home]]`.
    4. Do not include 'Home.md' or '_Sidebar.md' in the list of modules to group, but do include the Home link at the top.
    """
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return clean_markdown_response(response.text)

def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return

    if not os.path.exists(OUTPUT_DIR):
        print(f"Error: {OUTPUT_DIR} does not exist. Run generate_ai_wiki.py first.")
        return

    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    # 1. Read all existing module docs
    docs = read_markdown_files()
    if not docs:
        print("No module documentation found to organize.")
        return

    # 2. Generate Home.md
    try:
        home_content = generate_home_page(client, docs)
        with open(os.path.join(OUTPUT_DIR, "Home.md"), "w", encoding="utf-8") as f:
            f.write(home_content)
        print("Successfully wrote Home.md")
    except Exception as e:
        print(f"Error generating Home.md: {e}")

    # 3. Generate _Sidebar.md
    try:
        sidebar_content = generate_sidebar(client, docs)
        with open(os.path.join(OUTPUT_DIR, "_Sidebar.md"), "w", encoding="utf-8") as f:
            f.write(sidebar_content)
        print("Successfully wrote _Sidebar.md")
    except Exception as e:
        print(f"Error generating _Sidebar.md: {e}")

if __name__ == "__main__":
    main()
