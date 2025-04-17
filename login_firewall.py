import asyncio
import os
import time
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Error, TimeoutError

# Load .env file variables
load_dotenv()

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

async def login_firewall():
    username = os.getenv("FIREWALL_ID")
    password = os.getenv("FIREWALL_PASSWORD")
    url = "https://10.0.0.1:8090/httpclient.html"

    if not username or not password:
        print("❗ Username or password not found in .env file.")
        return False

    try:
        async with async_playwright() as p:
            print("🚀 Launching fast Chromium session...")

            user_data_dir = os.path.join(os.getcwd(), "firewall_user_data")
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=["--ignore-certificate-errors", "--disable-extensions"],
                ignore_https_errors=True,
            )
            page = context.pages[0] if context.pages else await context.new_page()

            print(f"🌐 Navigating to {url} ...")
            response = await page.goto(url, timeout=10000)

            if response:
                print(f"✅ Page loaded with status code: {response.status}")
            else:
                print("⚠️ No response received. Possible timeout or network error.")
                await context.close()
                return False

            print("⌨️ Filling credentials...")
            await page.fill("input[type='text']", username)
            await page.fill("input[type='password']", password)

            print("🔐 Submitting login form...")
            await page.click("#loginbutton", timeout=3000)

            print("✅ Login attempted successfully")
            await context.close()
            return True

    except TimeoutError as e:
        print(f"⏳ Timeout occurred: {e}")
        return False
    except Error as e:
        print(f"❌ Playwright error occurred: {e}")
        return False
    except Exception as ex:
        print(f"❗ Unexpected error: {ex}")
        return False

async def main():
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n🔁 Attempt {attempt} of {MAX_RETRIES}")
        success = await login_firewall()
        if success:
            print("🎉 Logged in successfully!")
            break
        elif attempt < MAX_RETRIES:
            print(f"🔄 Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            print("❌ All login attempts failed.")

if __name__ == "__main__":
    asyncio.run(main())
