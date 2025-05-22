import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def interact_with_page(driver, check_string, check_distance, send_email_callback):
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
                            f"Condition met: Distance {distance_value} <= {check_distance} in system: {row.text[0]}"
                        )
                        send_email_callback(
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
