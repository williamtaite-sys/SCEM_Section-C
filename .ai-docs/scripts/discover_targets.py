import os
import yaml
import glob
from pathlib import Path

# --- Bootstrap ---
# These paths are required to locate the configuration file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / ".ai-docs" / "config.yaml"

def load_yaml(path):
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}

def save_yaml(path, data):
    with open(path, 'w') as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

def get_available_templates(templates_dir_path):
    if not templates_dir_path.exists():
        return set()
    return {p.name for p in templates_dir_path.glob("*.md")}

def scan_repository_extensions(root_dir, known_extensions, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {'.git', '.ai-docs', 'node_modules', '__pycache__', '.ipynb_checkpoints'}
    
    found_extensions = set()
    
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            name_lower = file.lower()
            matched = False
            
            # Check for explicitly mapped extensions (longest match first)
            for ext in known_extensions:
                if name_lower.endswith(ext):
                    found_extensions.add(ext)
                    matched = True
            
    return found_extensions

def main():
    print(f"Initializing documentation config for: {PROJECT_ROOT}")

    # 1. Load existing config
    config = load_yaml(CONFIG_PATH)
    if 'targets' not in config:
        config['targets'] = []
    
    existing_target_names = {t.get('name') for t in config['targets']}
    
    # 2. Load Auto-Discovery Rules
    auto_discovery_rules = config.get('auto_discovery', {})
    if not auto_discovery_rules:
        print("No 'auto_discovery' rules found in config.yaml. Skipping auto-configuration.")
        return

    # 3. Identify available templates
    # Resolve templates_dir relative to PROJECT_ROOT
    templates_rel_path = config.get('templates_dir', '.ai-docs/templates')
    templates_dir = PROJECT_ROOT / templates_rel_path
    
    available_templates = get_available_templates(templates_dir)
    print(f"Found templates in {templates_rel_path}: {available_templates}")

    # 4. Scan repository for file types defined in auto_discovery
    sorted_extensions = sorted(auto_discovery_rules.keys(), key=len, reverse=True)
    found_extensions = scan_repository_extensions(PROJECT_ROOT, sorted_extensions)
    print(f"Found file types in repo: {found_extensions}")

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
            print(f"Warning: Template '{template_file}' needed for '{ext}' but not found in {templates_dir}")
            continue

        # Check if target already exists in config
        if target_name in existing_target_names:
            print(f"Skipping '{target_name}' (already configured)")
            continue

        # Add new target
        print(f"Adding configuration for: {target_name}")
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
        save_yaml(CONFIG_PATH, config)
        print(f"Successfully updated {CONFIG_PATH}")
    else:
        print("No changes needed. Config is up to date.")

if __name__ == "__main__":
    main()
