import logging
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
from smtplib import SMTP
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env file
load_dotenv()

URL = "https://www.eve-scout.com/#/"
CHECK_STRING = "Haimeh"  # Replace with your condition
CHECK_DISTANCE = 10  # Distance threshold


def setup_driver():
    """Set up the Selenium WebDriver with options."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)


def load_website(driver, url):
    """Load the website and return the driver."""
    logging.info(f"Loading website: {url}")
    driver.get(url)


def interact_with_page(driver, check_string, check_distance):
    """Interact with the page and perform the required checks."""
    try:
        # Wait for the input field to be visible and enabled
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "input-field"))
        )
        if not input_field.is_displayed() or not input_field.is_enabled():
            raise Exception("Input field is not interactable")

        # Enter the search term into the input field
        driver.execute_script(
            "arguments[0].value = arguments[1];", input_field, check_string
        )

        # Wait for the refresh button to be clickable
        refresh_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "refresh-button"))
        )
        if not refresh_button.is_displayed() or not refresh_button.is_enabled():
            raise Exception("Refresh button is not interactable")

        # Click the refresh button
        refresh_button.click()

        # Wait for the rows to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "datatable-row"))
        )

        # Locate all rows with the class "datatable-row"
        rows = driver.find_elements(By.CLASS_NAME, "datatable-row")
        logging.info(f"Found {len(rows)} rows.")

        # Check if the condition is met in any row
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")  # Get all columns in the row
            if len(columns) >= 3:  # Ensure the row has at least 3 columns
                distance = columns[2].text.strip()  # Get the third column (distance)
                try:
                    distance_value = float(distance)  # Convert distance to a float
                    if distance_value <= check_distance:
                        logging.info(
                            f"Condition met: Distance {distance_value} <= {check_distance} in row: {row.text}"
                        )
                        send_email(
                            subject="Condition Met on EVE Scout",
                            body=f"The condition '{check_string}' was found with distance {distance_value} in the data table.",
                        )
                        break
                except ValueError:
                    logging.warning(f"Invalid distance value: {distance}")
            else:
                logging.warning(f"Row does not have enough columns: {row.text}")

    except Exception as e:
        logging.error(f"Error interacting with the page: {e}")
        raise


def send_email(subject, body):
    """Send an email notification."""
    # Retrieve email credentials from environment variables
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT", email_user)
    try:
        if not email_user or not email_pass:
            raise Exception(
                "Email credentials are missing. Please set them in the .env file."
            )

        # Set up the SMTP server
        with SMTP("smtp.gmail.com", 587) as server:  # Replace with your SMTP server
            server.starttls()
            server.login(email_user, email_pass)

            # Create the email
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = email_user
            msg["To"] = recipient

            # Send the email
            server.sendmail(email_user, recipient, msg.as_string())
            logging.info("[+] Email sent successfully.")
    except Exception as e:
        logging.error(f"[!] Failed to send email: {e}")


def check_website(url, check_string, check_distance):
    """Main function to check the website."""
    with setup_driver() as driver:
        try:
            load_website(driver, url)
            interact_with_page(driver, check_string, check_distance)
        except Exception as e:
            logging.error(f"Error checking website: {e}")


# Execute the function once
if __name__ == "__main__":
    check_website(URL, CHECK_STRING, CHECK_DISTANCE)
