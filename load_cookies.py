# shopee_reviews_selenium_pagination.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
import csv
import json

# === CONFIG ===
PRODUCT_URL = "https://shopee.co.id/Baseus-Bowie-WM01-Upgrade-Edition-True-Wireless-Earphones-TWS-Mini-Earbuds-Earphone-Bluetooth-i.223032375.22768552611"

CHROME_USER_DATA_DIR = r"C:\Users\Asus\AppData\Local\Google\Chrome\User Data"
CHROME_PROFILE = "Default"

OUTPUT_CSV = "shopee_reviews.csv"
OUTPUT_JSON = "shopee_reviews.json"

# === SETUP CHROME WITH PROFILE ===
options = Options()
options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
options.add_argument(f"profile-directory={CHROME_PROFILE}")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# === OPEN PRODUCT PAGE ===
driver.get(PRODUCT_URL)
time.sleep(5)

# Scroll down to make reviews section visible
driver.execute_script("window.scrollTo(0, 800);")
time.sleep(2)

# Click "See All Reviews" if it exists
try:
    review_button = driver.find_element(By.XPATH, "//button[contains(., 'Lihat Semua Ulasan')]")
    review_button.click()
    time.sleep(3)
except:
    print("No 'See All Reviews' button found, maybe reviews already visible.")

reviews = []

page = 1
while True:
    print(f"Scraping page {page}...")

    # === SCRAPE REVIEWS ON CURRENT PAGE ===
    review_elements = driver.find_elements(By.CSS_SELECTOR, "div.shopee-comment-section__comment")

    for el in review_elements:
        try:
            username = el.find_element(By.CSS_SELECTOR, ".shopee-user-name").text
        except:
            username = ""
        try:
            rating = el.find_element(By.CSS_SELECTOR, ".shopee-rating-stars__rating").get_attribute("aria-label")
        except:
            rating = ""
        try:
            comment = el.find_element(By.CSS_SELECTOR, ".shopee-comment__content").text
        except:
            comment = ""
        reviews.append({
            "username": username,
            "rating": rating,
            "comment": comment
        })

    # === TRY CLICKING NEXT BUTTON ===
    try:
        next_button = driver.find_element(By.XPATH, "//button[contains(., '>')]")
        if "disabled" in next_button.get_attribute("class"):
            print("Reached last page of reviews.")
            break
        next_button.click()
        time.sleep(3)
        page += 1
    except (NoSuchElementException, ElementClickInterceptedException):
        print("No more next button found.")
        break

driver.quit()

# === SAVE REVIEWS ===
keys = ["username", "rating", "comment"]

# Save CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    writer.writerows(reviews)

# Save JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)

print(f"Scraping done! Collected {len(reviews)} reviews.")
print(f"Saved to {OUTPUT_CSV} and {OUTPUT_JSON}")
