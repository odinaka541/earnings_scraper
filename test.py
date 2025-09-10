# 541

"""
minimal Firefox test - debug step by step
"""

import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# debug logging
logging.basicConfig(level=logging.DEBUG)


def test_firefox_basic():
    """test basic Firefox functionality"""
    print("Testing Firefox WebDriver setup...")

    try:
        # creating ff options
        print("1. Creating Firefox options...")
        options = FirefoxOptions()
        options.add_argument("--headless")  # headless to avoid display issues

        # getting GeckoDriver
        print("2. Installing/finding GeckoDriver...")
        service = Service(GeckoDriverManager().install())

        # creating WebDriver
        print("3. Creating Firefox WebDriver...")
        driver = webdriver.Firefox(service=service, options=options)

        # testing navigation
        print("4. Testing navigation...")
        driver.get("https://www.google.com")

        # verifying it worked
        title = driver.title
        print(f"5. Success! Page title: {title}")

        # cleanup
        driver.quit()
        print("6. Test completed successfully!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_firefox_basic()