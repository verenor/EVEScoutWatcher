import tkinter as tk
from tkinter import messagebox
import logging
import schedule
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from page_interaction import interact_with_page
from email_utils import send_email
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

URL = "https://www.eve-scout.com/#/"
scheduler_thread = None  # Global variable to manage the scheduler thread
stop_scheduler = False  # Flag to stop the scheduler loop


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


def check_website(url, check_string, check_distance):
    """Main function to check the website."""
    with setup_driver() as driver:
        try:
            load_website(driver, url)
            interact_with_page(driver, check_string, check_distance, send_email)
        except Exception as e:
            logging.error(f"Error checking website: {e}")


def stop_script():
    """Stop the script by clearing the schedule and stopping the thread."""
    global stop_scheduler
    try:
        schedule.clear()  # Clear all scheduled tasks
        stop_scheduler = True  # Set the flag to stop the scheduler loop
        logging.info("Script stopped successfully.")
        messagebox.showinfo("Success", "Script stopped successfully!")
    except Exception as e:
        logging.error(f"Error stopping script: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")


def start_script(check_string_var, check_distance_var, interval_var):
    """Start the script with the provided values."""
    global scheduler_thread, stop_scheduler
    try:
        # Get values from the GUI
        check_string = check_string_var.get()
        check_distance = float(check_distance_var.get())
        interval_mins = int(interval_var.get())

        if not check_string:
            raise ValueError("CHECK_STRING cannot be empty.")
        if check_distance <= 0:
            raise ValueError("CHECK_DISTANCE must be greater than 0.")
        if interval_mins <= 0:
            raise ValueError("SCRIPT_EXECUTION_INTERVAL_MINS must be greater than 0.")

        # Schedule the script
        schedule.clear()  # Clear any existing schedules
        schedule.every(interval_mins).minutes.do(
            check_website, URL, check_string, check_distance
        )

        logging.info(f"Scheduled the script to run every {interval_mins} minutes.")
        messagebox.showinfo("Success", "Script started successfully!")

        # Run the scheduler in a loop
        def run_scheduler():
            global stop_scheduler
            while not stop_scheduler:
                schedule.run_pending()
                time.sleep(1)

        # Start the scheduler in a new thread
        stop_scheduler = False  # Reset the stop flag
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
    except Exception as e:
        logging.error(f"Error starting script: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")


def create_gui():
    """Create and display the GUI."""
    root = tk.Tk()
    root.title("Script Configuration")

    # Input fields
    tk.Label(root, text="System:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    check_string_var = tk.StringVar()
    tk.Entry(root, textvariable=check_string_var).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Desired Distance:").grid(
        row=1, column=0, padx=10, pady=5, sticky="e"
    )
    check_distance_var = tk.StringVar()
    tk.Entry(root, textvariable=check_distance_var).grid(
        row=1, column=1, padx=10, pady=5
    )

    tk.Label(root, text="Script Interval in Minutes:").grid(
        row=2, column=0, padx=10, pady=5, sticky="e"
    )
    interval_var = tk.StringVar()
    tk.Entry(root, textvariable=interval_var).grid(row=2, column=1, padx=10, pady=5)

    # Start button
    start_button = tk.Button(
        root,
        text="Start",
        command=lambda: start_script(
            check_string_var, check_distance_var, interval_var
        ),
    )
    start_button.grid(row=3, column=0, pady=10)

    # End button
    end_button = tk.Button(root, text="End", command=stop_script)
    end_button.grid(row=3, column=1, pady=10)

    # Run the GUI
    root.mainloop()


if __name__ == "__main__":
    create_gui()
