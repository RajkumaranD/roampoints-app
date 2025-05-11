from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime
from selenium.webdriver.common.keys import Keys


def get_delta_award_miles(origin, destination, departure_date):
    formatted_date = datetime.strptime(departure_date, "%Y-%m-%d").strftime("%a %b %d %Y")

    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://www.delta.com/")

    try:
        wait = WebDriverWait(driver, 30)

        # Ensure any modal container is gone before proceeding
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "modal-container")))
            print("Modal dismissed (container gone).")
        except:
            print("Modal still present, continuing anyway.")

        # Interact with origin
        from_input = wait.until(EC.element_to_be_clickable((By.ID, "fromAirportName")))
        from_input.clear()
        from_input.send_keys(origin)
        time.sleep(1)
        from_suggestion = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul[role='listbox'] li")))
        from_suggestion.click()
        time.sleep(1)

        # Interact with destination
        to_input = wait.until(EC.element_to_be_clickable((By.ID, "toAirportName")))
        to_input.clear()
        to_input.send_keys(destination)
        time.sleep(1)
        to_suggestion = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul[role='listbox'] li")))
        to_suggestion.click()
        time.sleep(1)

        # Click "Shop with Miles" checkbox label
        shop_with_miles_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='awardTravel']")))
        shop_with_miles_label.click()
        time.sleep(1)

        # Open calendar and select date
        calendar_input = wait.until(EC.element_to_be_clickable((By.ID, "input_departureDate_1")))
        calendar_input.click()
        time.sleep(2)

        aria_label = formatted_date  # e.g. "Fri Aug 15 2025"
        date_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{aria_label}']")))
        date_button.click()
        time.sleep(1)

        # Submit the search
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, "btnSubmit")))
        submit_button.click()

        # Wait for results to load
        time.sleep(20)

        all_elements = driver.find_elements(By.XPATH, "//*")
        miles_found = []

        for el in all_elements:
            try:
                text = el.text.strip()
                if re.match(r"^\d{1,3}(,\d{3})*$", text):
                    print("Potential miles candidate:", text)
                    miles_found.append(int(text.replace(",", "")))
            except:
                continue

        if miles_found:
            return min(miles_found)
        else:
            print("No numeric elements matched expected mileage pattern.")
            return None

    except Exception as e:
        print("Error:", e)
        return None
    finally:
        input("Press Enter to exit and close the browser...")
        driver.quit()


# Example test
if __name__ == "__main__":
    origin = "JFK"
    destination = "LAX"
    departure_date = "2025-08-15"
    miles = get_delta_award_miles(origin, destination, departure_date)
    print(f"Lowest Delta SkyMiles required: {miles}")
