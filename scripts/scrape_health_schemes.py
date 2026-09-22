import time
import os
import shutil
import json
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_backup(filename):
    if os.path.exists(filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'backups')
        
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
            
        backup_file = os.path.join(backup_folder, f"{os.path.basename(filename).replace('.json', '')}_{timestamp}.json")
        shutil.copy(filename, backup_file)
        print(f"Backed up {filename} to {backup_file}")

def get_chrome_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("window-size=1920,1080")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(options=opts)

def scrape_category(driver, category):
    scraped_data = []
    
    for page in range(1, category['pages'] + 1):
        print(f"  -> Fetching page {page} out of {category['pages']}...")
        
        url = f"https://www.india.gov.in/my-government/schemes/search?schemeCategory={category['id']}&schemeCategoryName={category['url_name']}&pagenumber={page}"
        driver.get(url)
        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
        except Exception:
            print(f"  -> Whoops, page {page} took too long to load or has no schemes. Moving on!")
            continue
            
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        for h2 in soup.find_all('h2'):
            link_tag = h2.find('a')
            if not link_tag:
                continue
                
            title = link_tag.text.strip()
            if not title:
                continue
                
            link = link_tag.get('href', '')
            if link and not link.startswith('http'):
                link = "https://www.india.gov.in" + link
                
            desc_tag = None
            tags_list = None
            
            for element in h2.find_all_next(['p', 'ul', 'h2']):
                if element.name == 'h2':
                    break 
                if element.name == 'p' and not desc_tag:
                    desc_tag = element
                if element.name == 'ul' and not tags_list:
                    tags_list = element
                    
                if desc_tag and tags_list:
                    break
                    
            description = desc_tag.text.strip() if desc_tag else ""
            
            tags = []
            if tags_list:
                tags = [li.text.strip() for li in tags_list.find_all('li') if li.text.strip()]
            
            scraped_data.append({
                'title': title,
                'link': link,
                'description': description,
                'tags': tags
            })
            
    return scraped_data

if __name__ == "__main__":
    print("Welcome! Starting the health schemes scraper...\n")
    
    health_category = {"name": "Health", "id": "5", "url_name": "Health%20%26%20Wellness", "pages": 31, "file": "health_wellness_schemes.json"}
    
    try:
        driver = get_chrome_driver()
        print(f"\n--- Now scraping the '{health_category['name']}' category ({health_category['pages']} pages) ---")
        
        schemes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        if not os.path.exists(schemes_dir):
            os.makedirs(schemes_dir)
            
        json_path = os.path.join(schemes_dir, health_category['file'])
        
        create_backup(json_path)
        
        data = scrape_category(driver, health_category)
        
        if data:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Awesome! Saved {len(data)} schemes to {json_path}")
        else:
            print(f"Hmm, no data was found for {health_category['name']}.")
            
    except Exception as e:
        print(f"Something went wrong: {e}")
    finally:
        print("\nAll done! Closing the browser.")
        driver.quit()
