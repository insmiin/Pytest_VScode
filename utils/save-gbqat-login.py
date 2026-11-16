# PURPOSE: This script is used to log in to the GBQAT website and save the authentication state for future use. 
# It uses Playwright to automate the browser interaction.
# run the command 'python -m utils.save-gbqat-login' to run the script to save the login state
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context()

    page = context.new_page()

    # Navigate to login page
    page.goto("https://qat.fraudsterkill.com/login")

    # Log in manually
    input("Complete login, then press Enter...")

    # Save authentication state
    context.storage_state(
        path="playwright/.auth/gbqat_login_state.json"
    )

    browser.close()