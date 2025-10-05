# shopee_reviews_selenium_pagination.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
import csv
import json
import pickle
import os
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# === CONFIG ===
PRODUCT_URL = "https://shopee.co.id/Baseus-BP1-Pro-TWS-Adaptive-ANC-Hi-Res-LDAC-50dB-6-Mic-ENC-with-IP55-55H-Earbud-Earphone-Bluetooth-6.0-i.223032375.43550697202"
COOKIE_FILE = "cookies.pkl"

# CHROME_USER_DATA_DIR = r"C:\Users\Asus\AppData\Local\Google\Chrome\User Data"
CHROME_USER_DATA_DIR = r"D:\chrome_selenium_profile"
CHROME_PROFILE = "Default"   # keep this as Default

OUTPUT_CSV = "shopee_reviews_3.csv"
OUTPUT_JSON = "shopee_reviews.json"

# === SETUP CHROME WITH PROFILE ===
options = Options()
# options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
# options.add_argument(f"profile-directory={CHROME_PROFILE}")
options.add_argument("--start-maximized")
# options.add_argument("--disable-session-crashed-bubble")   # 👈 disable restore popup
# options.add_argument("--no-first-run")
# options.add_argument("--no-default-browser-check")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# # driver = webdriver.Chrome(options=options)

driver = uc.Chrome(version_main=140, options=options)
driver.get("https://shopee.co.id/")
time.sleep(1)

with open("shopee_cookies.json", "r", encoding="utf-8") as f:
    cookies = json.load(f)

for cookie in cookies:
    # remove problematic keys
    cookie.pop("sameSite", None)
    cookie.pop("storeId", None)
    cookie.pop("id", None)
    try:
        driver.add_cookie(cookie)
    except Exception as e:
        print("Skipping cookie:", cookie.get("name"), "| Reason:", e)

# === RELOAD WITH COOKIES APPLIED ===
driver.get(PRODUCT_URL)
time.sleep(10)

print("✅ Should now be logged in and at product page")

review_section = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.shopee-product-comment-list"))
)

max_pages = 167
page_num = 1
all_reviews = []

while page_num <= max_pages:
    print(f"\n🔎 Scraping page {page_num} ...")
    time.sleep(1)  # give time for reviews to load

    # find all review items
    reviews = driver.find_elements(By.CSS_SELECTOR, "div.shopee-product-comment-list div[data-cmtid]")
    print(f"Found {len(reviews)} reviews on this page.")

    for i, review in enumerate(reviews, start=1):
        try:
            username = review.find_element(By.CSS_SELECTOR, "div.d72He7 > div").text.strip()
        except:
            username = "N/A"

        try:
            review_text = review.find_element(By.CSS_SELECTOR, "div.meQyXP, div.YNeDV").text.strip()
        except:
            review_text = "N/A"

        print(f"\nReview {i}:")
        print(f"User: {username}")
        print(f"Text: {review_text}")

        all_reviews.append({
            "user": username,
            "text": review_text
        })

    if page_num == max_pages:
        print("🚩 Reached max page limit. Stopping scrape.")
        break

    # check if next button exists & clickable
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "button.shopee-icon-button--right")
        if "disabled" in next_button.get_attribute("class"):
            print("🚩 No more pages. Scraping finished.")
            break
        else:
            next_button.click()
            page_num += 1
            time.sleep(1)
    except:
        print("🚩 Next button not found. Done.")
        break

# print total reviews collected
print(f"\n✅ Scraping complete! Collected {len(all_reviews)} reviews.")

driver.quit()

# === SAVE REVIEWS ===
keys = ["user", "text"]

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    writer.writerows(all_reviews)

print(f"💾 Reviews saved to {OUTPUT_CSV}")

# # Save JSON
# with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
#     json.dump(reviews, f, ensure_ascii=False, indent=2)

# print(f"Scraping done! Collected {len(reviews)} reviews.")
# print(f"Saved to {OUTPUT_CSV} and {OUTPUT_JSON}")
