from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5003"

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

try:
    # Test 1: Open the home page
    driver.get(BASE_URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("Test 1 passed: Store homepage opened.")

    # Test 2: Open the products page
    driver.get(BASE_URL + "/products")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("Test 2 passed: Products page opened.")

    # Test 3: Open the customer login page
    driver.get(BASE_URL + "/login")

    email = wait.until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    password = driver.find_element(By.NAME, "password")

    assert email.is_displayed()
    assert password.is_displayed()

    print("Test 3 passed: Customer login form is displayed.")

    print("\nAll Selenium tests passed!")

except Exception as e:
    print("Selenium test failed:", e)
    raise

finally:
    driver.quit()
