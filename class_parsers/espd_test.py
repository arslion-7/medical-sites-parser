from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to your ChromeDriver
service = Service('/usr/local/bin/chromedriver')  # Update this with the path to your ChromeDriver

# Initialize WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 1. Navigate to the Page
    driver.get('https://www.espd.info/journal-wiley')

    # 2. Wait for the cookie consent button to be clickable
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'cb-accept-all'))
    )

    # 3. Click the "Accept all" button
    accept_button = driver.find_element(By.ID, 'cb-accept-all')
    accept_button.click()

    # 4. Proceed with further actions on the page
    # Wait for the page to load or perform additional actions here
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'content-1552030810737'))
    )

    # Example: Clicking another button or interacting with the page
    button = driver.find_element(By.ID, 'content-1552030810737')
    button.click()

    # Optional: Extract content or take further actions after the click
    page_title = driver.title
    print(f"Page Title After Click: {page_title}")

    # Example: Extract some content
    content = driver.find_element(By.CSS_SELECTOR, 'body').text
    print(content[:1000])  # Print the first 1000 characters of the content

    # Pause the script to keep the browser open for manual inspection
    input("Press Enter to close the browser...")

finally:
    # Clean up and close the browser
    driver.quit()