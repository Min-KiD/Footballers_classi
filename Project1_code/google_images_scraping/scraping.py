from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import io
from PIL import Image
import time
import os
import hashlib

# Chrome Version 117.0.5938.92 (Official Build) (64-bit)

wd = webdriver.Chrome

def download_image(download_path: str, url: str):
    try:
        image_content = requests.get(url).content
        image_bytes = io.BytesIO(image_content)
        image = Image.open(image_bytes)
        # turn path for each image uniquely
        file_path = os.path.join(download_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
       
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG")
            
        print('Success')
    except Exception as e:
        print('Failed ', e)

def get_google_image_urls(name: str, wd, delay: float, max_images: int):
    def scroll_down(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)
    
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={s}&oq={s}&gs_l=img"

    wd.get(search_url.format(s=name))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_images:
        scroll_down(wd)

        thumbnail_results = wd.find_elements(By.CLASS_NAME, "Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start+1} to {number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            try:
                img.click()
                time.sleep(delay)
            except Exception:
                continue
  
            actual_images = wd.find_elements(By.CLASS_NAME, "iPVvYb")
            
            # usually len(actual_images) should = 1, can not find another result yet
            
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if image_count >= max_images:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        if image_count < max_images:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            load_more_button = wd.find_elements(By.CLASS_NAME,"LZ4I")
            if load_more_button:
                wd.execute_script("document.querySelector('.LZ4I').click();")

        results_start = len(thumbnail_results)

    return image_urls

def search_and_download(search_term: str, number_images: int, target_path= './images'):
    target_folder = os.path.join(target_path,' '.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome() as wd:
        urls = get_google_image_urls(search_term, wd=wd, delay=0.5, max_images=number_images)
        
    try: 
        for url in urls:
            download_image(target_folder, url)
    except Exception as e:
        print(e)
        
footballers = ["Lionel Messi", "Cristiano Ronaldo", "Neymar", "Kylian Mbappé", "Kevin De Bruyne",
               "Virgil van Dijk", "David Beckham", "Erling Haaland", "Alisson Becker", "N'Golo Kanté"]

for f in footballers:
    search_and_download(f + " face photo", 100)

# wd.quit()

