import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright
import os

url = "https://1drv.ms/x/c/019ebf93eb1529d0/IQD2itTtsBcWRKAdyQCkEPOPARq7A4hGwcOGNmAQY0HEwd8?e=UAgWRE"
dest_path = os.path.abspath("data/INV_OCTUBRE_11.xlsx")
os.makedirs("data", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    
    print(f"Navigating to {url}...")
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    
    print("Page title:", page.title())
    print("Current URL:", page.url)
    
    # Check if download link exists or click Download/File -> Download
    # Many Excel Online pages have File or Download button or direct download link
    # Look for button or link with 'Descargar' or 'Download'
    download_btn = page.locator("button:has-text('Descargar'), a:has-text('Descargar'), button:has-text('Download'), a:has-text('Download'), [aria-label*='Descargar'], [aria-label*='Download']")
    
    saved = False
    if download_btn.count() > 0:
        print(f"Found {download_btn.count()} download buttons/links")
        for i in range(download_btn.count()):
            btn = download_btn.nth(i)
            print(f"Btn {i}: text='{btn.text_content().strip()}', visible={btn.is_visible()}")
            if btn.is_visible():
                try:
                    with page.expect_download(timeout=10000) as download_info:
                        btn.click()
                    download = download_info.value
                    download.save_as(dest_path)
                    print(f"SUCCESS: Saved download to {dest_path}")
                    saved = True
                    break
                except Exception as e:
                    print(f"Click failed: {e}")
                    
    if not saved:
        # Check if URL can be modified with action=download
        cur_url = page.url
        print("Trying direct download URL manipulation on:", cur_url)
        # In OneDrive, changing &action=default to &action=download or appending &download=1
        if "action=" in cur_url:
            dl_url = cur_url.replace("action=default", "action=download").replace("action=view", "action=download")
        else:
            dl_url = cur_url + "&action=download"
            
        try:
            with page.expect_download(timeout=15000) as download_info:
                page.goto(dl_url)
            download = download_info.value
            download.save_as(dest_path)
            print(f"SUCCESS via action=download: Saved to {dest_path}")
            saved = True
        except Exception as e:
            print(f"Action download failed: {e}")
            
    browser.close()
    
if os.path.exists(dest_path):
    print(f"File exists! Size: {os.path.getsize(dest_path)} bytes")
else:
    print("File was not downloaded yet.")

