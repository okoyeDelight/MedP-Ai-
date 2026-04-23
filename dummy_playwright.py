from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8501")
    # Wait for Streamlit to render
    page.wait_for_selector('div[data-testid="stChatInput"]', timeout=10000)
    print("Found stChatInput!")

    # Get HTML to check its structure
    el = page.locator('div[data-testid="stChatInput"]')
    print(el.inner_html())
    browser.close()
