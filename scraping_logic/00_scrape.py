import os
import sys
import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DOMAIN_URL, API_URL, RAW_DATA_DIR, START, END

os.makedirs(RAW_DATA_DIR, exist_ok=True)
print(f'Total blocks to fetch: {END - START}')

JS_FETCH_AND_RETURN = '''
    const callback = arguments[arguments.length - 1];
    const apiUrl   = arguments[0];
    
    fetch(apiUrl)
      .then(response => {
          if (!response.ok) {
              callback('ERROR_STATUS_' + response.status);
          } else {
              return response.json();
          }
      })
      .then(jsonData => {
          if (typeof jsonData !== 'string') {
              callback(JSON.stringify(jsonData));
          }
      })
      .catch(err => {
          callback('FETCH_EXCEPTION_' + err.toString());
      });
'''

def main(start_block: int, end_block: int):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--log-level=3")
    options.add_argument("--headless")           # <-- Headless mode enabled
    options.add_argument("--disable-gpu")        # Recommended alongside headless
    options.add_argument("--no-sandbox")         # Required in some environments
    options.add_argument("--window-size=720,480")  # Ensure a reasonable viewport

    chrome_service = Service(log_path=os.devnull)

    driver = webdriver.Chrome(service=chrome_service, options=options)
    driver.get(DOMAIN_URL.format(block_num=start_block))

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )

    try:
        for block_num in tqdm(range(start_block, end_block)):
            output_path = os.path.join(RAW_DATA_DIR, f'{block_num}.json')
            if os.path.exists(output_path):
                continue

            api_url  = API_URL.format(block_num=block_num)
            
            try:
                json_text = driver.execute_async_script(JS_FETCH_AND_RETURN, api_url)

                if isinstance(json_text, str):
                    if json_text.startswith('ERROR_STATUS_') or json_text.startswith('FETCH_EXCEPTION_'):
                        continue

                try:
                    data = json.loads(json_text)
                except json.JSONDecodeError as e:
                    print(f'[Block {block_num}] JSON decode error: {e}')
                    continue

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

            except Exception as _:
                continue
    finally:
        driver.quit()

if __name__ == '__main__':
    main(START, END)