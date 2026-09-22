import json
import os
import shutil

def convert_scraped_to_valid_schema(item):
    """Converts a scraper dict to the SmartGov valid schema."""
    desc = item.get("description", "No description provided.")
    return {
        "category": "Health & Wellness",
        "level": "National",
        "icon": "hospital",
        "original_complex_text": desc,
        "required_documents": ["Aadhaar Card", "Identity Proof"],
        "source_url": item.get("link", ""),
        "keywords": item.get("tags", []),
        "simplified": {
            "eligibility": "Please refer to the official guidelines for specific eligibility criteria.",
            "benefits": desc,
            "documents": "Aadhaar Card, Identity Proof.",
            "steps": "Visit the official website to apply or learn more."
        },
        "telugu": {
            "eligibility": "నిర్దిష్ట అర్హత ప్రమాణాల కోసం దయచేసి అధికారిక మార్గదర్శకాలను చూడండి.",
            "benefits": "దయచేసి అధికారిక వెబ్‌సైట్ చూడండి.",
            "documents": "ఆధార్ కార్డు, గుర్తింపు కార్డు.",
            "steps": "దరఖాస్తు చేయడానికి లేదా మరింత తెలుసుకోవడానికి అధికారిక వెబ్‌సైట్‌ను సందర్శించండి."
        }
    }

def merge_all_schemes():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    backup_dir = os.path.join(data_dir, 'backups')
    
    os.makedirs(backup_dir, exist_ok=True)
    
    merged_schemes = {}
    files_to_remove = []
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".json") and filename not in {"scheme_schema.json", "facilities.json", "merged_schemes.json"}:
            filepath = os.path.join(data_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
                    continue
                    
            if isinstance(data, dict):
                print(f"Loaded {len(data)} schemes from dict file: {filename}")
                merged_schemes.update(data)
                files_to_remove.append(filepath)
            elif isinstance(data, list):
                print(f"Converting and loading {len(data)} schemes from list file: {filename}")
                for item in data:
                    title = item.get("title")
                    if title:
                        merged_schemes[title] = convert_scraped_to_valid_schema(item)
                files_to_remove.append(filepath)
                
    # Save the merged catalog
    merged_path = os.path.join(data_dir, 'merged_schemes.json')
    with open(merged_path, 'w', encoding='utf-8') as f:
        json.dump(merged_schemes, f, ensure_ascii=False, indent=2)
        
    print(f"\nSuccessfully merged into 'merged_schemes.json' with {len(merged_schemes)} total schemes.")
    
    # Backup and remove old files
    for filepath in files_to_remove:
        filename = os.path.basename(filepath)
        backup_path = os.path.join(backup_dir, filename)
        shutil.copy(filepath, backup_path)
        os.remove(filepath)
        print(f"Backed up and removed old file: {filename}")

if __name__ == "__main__":
    merge_all_schemes()
