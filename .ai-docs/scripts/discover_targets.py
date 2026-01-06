import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Set, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Bootstrap ---
# These paths are required to locate the configuration file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / ".ai-docs" / "config.yaml"

# Default directories to ignore during scanning
DEFAULT_IGNORE_DIRS = {'.git', '.ai-docs', 'node_modules', '__pycache__', '.ipynb_checkpoints', 'venv', '.venv'}

def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file, returning empty dict if not found."""
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except (yaml.YAMLError, IOError) as e:
        logging.error(f"Failed to load {path}: {e}")
        return {}

def save_yaml(path: Path, data: Dict[str, Any]) -> bool:
    """Save data to YAML file. Returns True on success."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        return True
    except (yaml.YAMLError, IOError) as e:
        logging.error(f"Failed to save {path}: {e}")
        return False

def get_available_templates(templates_dir_path: Path) -> Set[str]:
    """Get set of available template filenames."""
    if not templates_dir_path.exists():
        logging.warning(f"Templates directory not found: {templates_dir_path}")
        return set()
    return {p.name for p in templates_dir_path.glob("*.md")}

def scan_repository_extensions(
    root_dir: Path,
    known_extensions: list,
    ignore_dirs: Optional[Set[str]] = None
) -> Set[str]:
    """
    Scan repository for files matching known extensions.

    Args:
        root_dir: Root directory to scan
        known_extensions: List of file extensions to look for (e.g., ['.sql', '.py'])
        ignore_dirs: Set of directory names to skip

    Returns:
        Set of found extensions
    """
    if ignore_dirs is None:
        ignore_dirs = DEFAULT_IGNORE_DIRS

    found_extensions: Set[str] = set()

    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            name_lower = file.lower()

            # Check for explicitly mapped extensions (longest match first)
            for ext in known_extensions:
                if name_lower.endswith(ext):
                    found_extensions.add(ext)

    return found_extensions

def main() -> None:
    logging.info(f"Initializing documentation config for: {PROJECT_ROOT}")

    # 1. Load existing config
    config = load_yaml(CONFIG_PATH)
    if not config:
        logging.error("Could not load config.yaml. Please ensure it exists.")
        return

    # Ensure targets is a list (handle None from empty YAML key)
    if config.get('targets') is None:
        config['targets'] = []

    existing_target_names: Set[str] = {t.get('name') for t in config['targets'] if t.get('name')}

    # 2. Load Auto-Discovery Rules
    auto_discovery_rules: Dict[str, Dict[str, str]] = config.get('auto_discovery', {})
    if not auto_discovery_rules:
        logging.info("No 'auto_discovery' rules found in config.yaml. Skipping auto-configuration.")
        return

    # 3. Identify available templates
    templates_rel_path = config.get('templates_dir', '.ai-docs/templates')
    templates_dir = PROJECT_ROOT / templates_rel_path

    available_templates = get_available_templates(templates_dir)
    logging.info(f"Found templates in {templates_rel_path}: {available_templates}")

    # 4. Scan repository for file types defined in auto_discovery
    sorted_extensions = sorted(auto_discovery_rules.keys(), key=len, reverse=True)
    found_extensions = scan_repository_extensions(PROJECT_ROOT, sorted_extensions)
    logging.info(f"Found file types in repo: {found_extensions}")

    # 5. Update targets
    changes_made = False
    for ext in found_extensions:
        if ext not in auto_discovery_rules:
            continue

        rule = auto_discovery_rules[ext]
        template_file = rule.get('template')
        category = rule.get('category', 'Uncategorized')
        target_name = rule.get('target_name', f"Files ({ext})")

        # Check if template actually exists
        if template_file not in available_templates:
            logging.warning(f"Template '{template_file}' needed for '{ext}' not found in {templates_dir}")
            continue

        # Check if target already exists in config
        if target_name in existing_target_names:
            logging.debug(f"Skipping '{target_name}' (already configured)")
            continue

        # Add new target
        logging.info(f"Adding configuration for: {target_name}")
        new_target = {
            "name": target_name,
            "pattern": f"**/*{ext}",
            "template": template_file,
            "category": category
        }
        config['targets'].append(new_target)
        existing_target_names.add(target_name)
        changes_made = True

    # 6. Save if changes
    if changes_made:
        if save_yaml(CONFIG_PATH, config):
            logging.info(f"Successfully updated {CONFIG_PATH}")
        else:
            logging.error(f"Failed to save changes to {CONFIG_PATH}")
    else:
        logging.info("No changes needed. Config is up to date.")

if __name__ == "__main__":
    main()
