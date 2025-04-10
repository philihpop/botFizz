import time
import traceback
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

class FizzScraper:

    def __init__(self):
        self.fizz_url = "https://the-fizz.com/en/search-nl/?searchcriteria=BUILDING:THE_FIZZ_LEIDEN;AREA:LEIDEN;" # Leiden as an example
        
        options = webdriver.ChromeOptions()
        options.add_argument("window-size=1920x1480")
        options.add_argument("disable-dev-shm-usage")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        # Added for Linux environments
        options.add_argument("--remote-debugging-port=9222")
        
        try:
            # Check if ChromeDriver path is specified
            if 'CHROMEDRIVER_PATH' in os.environ:
                chromedriver_path = os.environ['CHROMEDRIVER_PATH']
                print(f"Using specified ChromeDriver path: {chromedriver_path}")
                service = Service(executable_path=chromedriver_path)
                self.browser = webdriver.Chrome(service=service, options=options)
            else:
                # Default - let Selenium find ChromeDriver
                print("Using default ChromeDriver")
                self.browser = webdriver.Chrome(options=options)
            
        except Exception as e:
            print(f"Error initializing Chrome WebDriver: {str(e)}")
            traceback.print_exc()
            sys.exit(1)  # Exit if we can't initialize the browser

    def close(self):
        """Close the browser."""
        if hasattr(self, 'browser'):
            self.browser.quit()

    def check_availability(self):
        """
        Checks if rooms are available on The Fizz Leiden.
        Returns a dictionary with availability status and details.
        """
        try:
            # Load the page
            print(f"Accessing URL: {self.fizz_url}")
            self.browser.get(self.fizz_url)
            time.sleep(5)  # Increased wait time for better reliability
            
            # Print page title for debugging
            print(f"Page title: {self.browser.title}")
            
            # Check for the "fully booked" message
            page_source = self.browser.page_source
            fully_booked_text = "We are currently fully booked."
            
            # Debug: Print a snippet of the page source
            print(f"Page source snippet: {page_source[:200]}...")
            
            # If the message is not found, rooms may be available
            if fully_booked_text not in page_source:
                print("Fully booked message not found! Rooms might be available.")
                try:
                    # Save screenshot in a directory that should always be writable
                    screenshot_path = os.path.join(os.path.expanduser("~"), "fizz_available.png")
                    self.browser.save_screenshot(screenshot_path)
                    print(f"Screenshot saved to {screenshot_path}")
                except Exception as screenshot_error:
                    print(f"Could not save screenshot: {str(screenshot_error)}")
                
                return {
                    "available": True,
                    "url": self.fizz_url,
                    "message": "The 'fully booked' message is not present. Rooms might be available!"
                }
            else:
                print("Still fully booked.")
                return {
                    "available": False,
                    "url": self.fizz_url,
                    "message": "The Fizz Leiden is currently fully booked."
                }
            
        except Exception as e:
            error_msg = f"Error checking The Fizz Leiden: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return {
                "available": False, 
                "url": self.fizz_url, 
                "error": error_msg
            }


if __name__ == "__main__":
    scraper = None
    try:
        scraper = FizzScraper()
        result = scraper.check_availability()
        print(result)
    except Exception as e:
        print(f"Main error: {str(e)}")
        traceback.print_exc()
    finally:
        if scraper:
            scraper.close()