import os
import sys
import yaml
import glob
from google import genai

# Constants
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config.yaml")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")

def load_config():
    """Loads the config.yaml file."""
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config file not found at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def load_template(template_name):
    """Loads a markdown template from the templates directory."""
    path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(path):
        # Fallback to generic if specific not found, or error
        print(f"Warning: Template {template_name} not found. Using generic.")
        return "Analyze this file: {{filename}}\n\n{{content}}"
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

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

def generate_docs(client, model, content, filename, template_text):
    """Calls Gemini API."""
    # Simple formatting injection
    # In a real production system, use jinja2 for robust templating
    prompt = template_text.replace("{{filename}}", filename).replace("{{content}}", content[:100000])
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return clean_markdown_response(response.text)
    except Exception as e:
        print(f"API Error for {filename}: {e}")
        return None

def main():
    config = load_config()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    output_dir = config.get("wiki_dir", "wiki_content")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Starting Documentation Generation for: {config.get('project_name')}")

    processed_files = []

    for target in config.get("targets", []):
        pattern = target.get("pattern")
        template_name = target.get("template")
        category = target.get("category", "General")
        
        # Recursive glob
        files = glob.glob(pattern, recursive=True)
        
        # Simple ignore check (can be improved with fnmatch)
        ignore_patterns = config.get("ignore_patterns", [])
        
        for file_path in files:
            # Skip if matched ignore (naive implementation)
            if any(ign in file_path for ign in ignore_patterns):
                continue
            
            # Skip if directory
            if os.path.isdir(file_path):
                continue

            print(f"Processing {file_path} using {template_name}...")
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                template = load_template(template_name)
                doc_content = generate_docs(client, config.get("model", "gemini-2.5-flash"), content, file_path, template)
                
                if doc_content:
                    # Create a flat filename for wiki: "folder_subfolder_filename.md"
                    # or keep hierarchy? Wikis are usually flat. Let's do flat with underscores.
                    safe_name = file_path.replace("\\", "_").replace("/", "_").replace(".", "_") + ".md"
                    output_path = os.path.join(output_dir, safe_name)
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(f"<!-- Category: {category} -->\n")
                        f.write(f"<!-- Source: {file_path} -->\n\n")
                        f.write(doc_content)
                    
                    processed_files.append(file_path)
                    print(f"Saved to {output_path}")
            
            except Exception as e:
                print(f"Failed to process {file_path}: {e}")

    print(f"Completed. Processed {len(processed_files)} files.")

if __name__ == "__main__":
    main()
