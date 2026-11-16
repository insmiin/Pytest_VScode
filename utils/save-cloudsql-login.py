from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        "./chrome-profile",
        channel="chrome",
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://console.cloud.google.com/")

    input("Log in fully (password + authenticator), then press Enter here...")

    context.storage_state(path="playwright/.auth/googlecloudsql.json")
    print("Saved to playwright/.auth/googlecloudsql.json")
    context.close()