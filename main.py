import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import os
import requests
from selenium.common.exceptions import JavascriptException
import urllib.parse
from collections import Counter
from datetime import datetime
from selenium.webdriver.chrome.service import Service

NUM_ARTICLES = 5

def get_unique_txt_filename(folder=".", prefix="txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(folder, f"{prefix}_{timestamp}.txt")
    
def log(msg):
    with open(log_file_name, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def makeCall(url, script, default):
    response = default
    try:
        driver.get(url)
        time.sleep(2)  
        while response == default:
            try:
                response = driver.execute_script(script)
            except JavascriptException:
                break
    except NoSuchElementException:
        log("NoSuchElementException: Element not found")

    if response:
        return response
    else:
        return 'Not Available'

def googleTranslate(src, trg, phrase):
    encoded_phrase = urllib.parse.quote(phrase)
    url = f'https://translate.google.com/?sl={src}&tl={trg}&text={encoded_phrase}&op=translate'
    
    script = 'return document.querySelector(".ryNqvb").textContent'
    return makeCall(url, script, None)


# options = ChromeOptions()
# driver = webdriver.Chrome(options=options)
options = ChromeOptions()
service = Service(
    r"C:/Users/user/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
)
driver = webdriver.Chrome(service=service, options=options)
# driver.maximize_window()
os.makedirs("cover_images", exist_ok=True)

log_file_name = get_unique_txt_filename()

title_headers = []
translated_headers = []

executor_object = {
    'action': 'setSessionName',
    'arguments': {
        'name': "Assignment Test"
    }
}
browserstack_executor = 'browserstack_executor: {}'.format(json.dumps(executor_object))
driver.execute_script(browserstack_executor)


try:
    driver.get('https://elpais.com/')

    # Wait until page loads
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "html"))
    )

    # Detect page language
    html_lang = driver.find_element(By.TAG_NAME, "html").get_attribute("lang")
    log(f"Detected page language: {html_lang}")

    if html_lang and html_lang.startswith("es"):
        log("The website declares Spanish as its language.")
    else:
        log("The website does NOT declare Spanish as its language.")

    # Accept cookies
    try:
        consent_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        consent_button.click()
        log("Clicked consent button.")
    except TimeoutException:
        log("Consent button not found or already accepted.")

    # Go to Opinión section
    opinion = "//a[contains(@href, '/opinion')]"
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, opinion))
    ).click()

    # Wait for articles to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//main//article"))
    )

    # Collect hrefs of all articles
    article_links = []
    all_article_elems = driver.find_elements(By.XPATH, "//main//article//header//h2//a")
    for a in all_article_elems:
        href = a.get_attribute("href")
        if href:
            article_links.append(href)

    log(f"\nFound {len(article_links)} articles. Fetching first {NUM_ARTICLES}...\n")

    for index, article_link in enumerate(article_links[:NUM_ARTICLES], start=1):
        log(f"\nOpening Article {index}: {article_link}")
        driver.get(article_link)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            title = driver.find_element(By.TAG_NAME, "h1").text
            log(f"Article {index} Title: {title}")

            title_headers.append(title)

        except TimeoutException:
            log("Article title not found.")
            continue

        # Fetch first paragraph
        try:
            time.sleep(5)
            content = driver.find_element(By.XPATH, "//article//p[1]").text
            log(f"Content: {content}\n")
        except NoSuchElementException:
            log("No paragraph content found.\n")

        # Download cover image if available
        try:
            time.sleep(5)
            img_elem = driver.find_element(By.XPATH, "//article//img")
            img_url = img_elem.get_attribute("src")
            img_data = requests.get(img_url).content
            img_filename = f"cover_images/article_{index}.jpg"
            with open(img_filename, "wb") as handler:
                handler.write(img_data)
            log(f"Image saved: {img_filename}\n")
        except NoSuchElementException:
            log("No cover image found.\n")

    driver.execute_script(
             'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Test Successfully Completed"}}')

except Exception as e:
    log(f"Test failed due to unexpected error: {e}")
    driver.execute_script(
             'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Test Failed due to an exception"}}')


finally:

    for title in title_headers:
        title_en = googleTranslate("es", "en", title)
        log(f"Original Title (ES) {title}\nTranslated Title (EN): {title_en}\n")
    # Combine all translated headers into a single string
    all_text = " ".join(translated_headers)

    # Tokenize and count words (ignore case)
    words = all_text.lower().split()
    word_counts = Counter(words)

    # Find words repeated more than twice
    repeated_words = {word: count for word, count in word_counts.items() if count > 2}

    # Print analysis
    log("\n=== Repeated Words in Translated Headers ===")
    if repeated_words:
        for word, count in repeated_words.items():
            log(f"{word}: {count}")
    else:
        log("No words repeated more than twice.")
    # Stop the driver
    driver.quit()
    log("Test finished and browser closed.")
