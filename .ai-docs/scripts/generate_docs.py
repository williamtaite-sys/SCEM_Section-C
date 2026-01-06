import os
import sys
import yaml
import glob
import argparse
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config.yaml")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")
MAX_FILE_SIZE_BYTES = 500_000  # 500KB - warn if file exceeds this
MAX_CONTENT_CHARS = 100_000   # Truncate content sent to LLM

# --- LLM Provider Abstraction ---

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: str) -> str:
        pass

class GoogleProvider(LLMProvider):
    def __init__(self, api_key: str):
        try:
            from google import genai
            self.client = genai.Client(api_key=api_key)
        except ImportError:
            logging.error("'google-genai' library not installed. Please run 'pip install google-genai'.")
            sys.exit(1)

    def generate(self, prompt: str, model: str) -> str:
        response = self.client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            logging.error("'openai' library not installed. Please run 'pip install openai'.")
            sys.exit(1)

    def generate(self, prompt: str, model: str) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            logging.error("'anthropic' library not installed. Please run 'pip install anthropic'.")
            sys.exit(1)

    def generate(self, prompt: str, model: str) -> str:
        response = self.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

def get_llm_provider(config: Dict[str, Any]) -> LLMProvider:
    """Factory function to create the appropriate LLM provider."""
    provider_name = config.get("provider", "google").lower()

    if provider_name == "google":
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logging.error("GOOGLE_API_KEY environment variable not set.")
            sys.exit(1)
        return GoogleProvider(api_key)

    elif provider_name == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logging.error("OPENAI_API_KEY environment variable not set.")
            sys.exit(1)
        return OpenAIProvider(api_key)

    elif provider_name == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logging.error("ANTHROPIC_API_KEY environment variable not set.")
            sys.exit(1)
        return AnthropicProvider(api_key)

    else:
        logging.error(f"Unsupported provider '{provider_name}'. Supported: google, openai, anthropic.")
        sys.exit(1)

# --- Helper Functions ---

def load_config() -> Dict[str, Any]:
    """Loads the config.yaml file."""
    if not os.path.exists(CONFIG_PATH):
        logging.error(f"Config file not found at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def load_template(template_name: str) -> str:
    """Loads a markdown template from the templates directory."""
    path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(path):
        logging.warning(f"Template {template_name} not found. Using generic fallback.")
        return "Analyze this file: {{filename}}\n\n{{content}}"

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def clean_markdown_response(text: Optional[str]) -> str:
    """Removes markdown code fences if present."""
    if not text:
        return ""
    text = text.strip()
    # Remove ```markdown or ``` if it wraps the entire response
    if text.startswith("```markdown"):
        text = text[11:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def should_skip_file(file_path: str, ignore_patterns: List[str]) -> bool:
    """Check if file matches any ignore pattern."""
    for pattern in ignore_patterns:
        if pattern in file_path:
            return True
    return False

def get_file_size_warning(file_path: str) -> Optional[str]:
    """Returns a warning message if file is large, None otherwise."""
    try:
        size = os.path.getsize(file_path)
        if size > MAX_FILE_SIZE_BYTES:
            return f"Large file ({size / 1024:.1f}KB) - content will be truncated"
    except OSError:
        pass
    return None

# --- Main Logic ---

def main():
    parser = argparse.ArgumentParser(description="Generate AI-powered documentation from source code.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview files that would be processed without calling LLM or writing output"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = load_config()

    # Initialize Provider (skip in dry-run mode)
    llm = None
    if not args.dry_run:
        llm = get_llm_provider(config)

    model = config.get("model", "gemini-2.5-flash")
    output_dir = config.get("wiki_dir", "wiki_content")

    if not args.dry_run and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    project_name = config.get('project_name', 'Unknown Project')
    provider_name = config.get('provider', 'google')

    logging.info(f"{'[DRY RUN] ' if args.dry_run else ''}Starting Documentation Generation")
    logging.info(f"Project: {project_name}")
    if not args.dry_run:
        logging.info(f"Provider: {provider_name} | Model: {model}")

    processed_files: List[str] = []
    skipped_files: List[str] = []

    # Ensure targets is iterable (handle None from YAML)
    targets: List[Dict[str, Any]] = config.get("targets") or []
    ignore_patterns: List[str] = config.get("ignore_patterns", [])

    if not targets:
        logging.warning("No targets configured. Run discover_targets.py first or add targets to config.yaml")
        return

    for target in targets:
        pattern = target.get("pattern")
        template_name = target.get("template")
        category = target.get("category", "General")
        target_name = target.get("name", pattern)

        logging.info(f"Processing target: {target_name} (pattern: {pattern})")

        # Recursive glob
        files = glob.glob(pattern, recursive=True)

        for file_path in files:
            # Skip directories
            if os.path.isdir(file_path):
                continue

            # Skip ignored files
            if should_skip_file(file_path, ignore_patterns):
                logging.debug(f"Skipping (ignore pattern): {file_path}")
                skipped_files.append(file_path)
                continue

            # Check file size
            size_warning = get_file_size_warning(file_path)
            if size_warning:
                logging.warning(f"{file_path}: {size_warning}")

            if args.dry_run:
                logging.info(f"  [WOULD PROCESS] {file_path} -> {category}/{template_name}")
                processed_files.append(file_path)
                continue

            logging.info(f"Processing: {file_path}")

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                template = load_template(template_name)
                # Template substitution with content truncation
                prompt = template.replace("{{filename}}", file_path).replace("{{content}}", content[:MAX_CONTENT_CHARS])

                # Call LLM
                response_text = llm.generate(prompt, model)
                doc_content = clean_markdown_response(response_text)

                if doc_content:
                    # Create a flat filename for wiki: "folder_subfolder_filename.md"
                    safe_name = file_path.replace("\\", "_").replace("/", "_").replace(".", "_") + ".md"
                    output_path = os.path.join(output_dir, safe_name)

                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(f"<!-- Category: {category} -->\n")
                        f.write(f"<!-- Source: {file_path} -->\n\n")
                        f.write(doc_content)

                    processed_files.append(file_path)
                    logging.info(f"  Saved: {output_path}")
                else:
                    logging.warning(f"  Empty response for {file_path}")

            except (IOError, OSError) as e:
                logging.error(f"Failed to read {file_path}: {e}")
            except Exception as e:
                logging.error(f"Failed to process {file_path}: {e}")

    # Summary
    logging.info("=" * 50)
    if args.dry_run:
        logging.info(f"[DRY RUN] Would process {len(processed_files)} files")
        logging.info(f"[DRY RUN] Would skip {len(skipped_files)} files (ignore patterns)")
    else:
        logging.info(f"Completed. Processed {len(processed_files)} files.")
        if skipped_files:
            logging.info(f"Skipped {len(skipped_files)} files (ignore patterns).")

if __name__ == "__main__":
    main()
