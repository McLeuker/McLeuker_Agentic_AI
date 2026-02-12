#!/usr/bin/env python3
"""
Playwright Installation Verification Script
============================================

This script verifies that Playwright and Chromium are properly installed
and can be used for browser automation on Railway.

Run this after deployment to verify the setup.
"""

import asyncio
import sys
import os

def check_environment():
    """Check environment variables."""
    print("=== Environment Variables ===")
    print(f"PLAYWRIGHT_BROWSERS_PATH: {os.getenv('PLAYWRIGHT_BROWSERS_PATH', 'NOT SET')}")
    print(f"PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: {os.getenv('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD', 'NOT SET')}")
    print()

async def test_playwright():
    """Test Playwright browser launch."""
    print("=== Testing Playwright ===")
    
    try:
        from playwright.async_api import async_playwright
        print("✓ Playwright module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Playwright: {e}")
        return False
    
    try:
        async with async_playwright() as p:
            print("✓ Playwright context created")
            
            # Try to launch Chromium
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ]
            )
            print("✓ Chromium browser launched successfully")
            
            # Create a page
            page = await browser.new_page(viewport={"width": 1280, "height": 720})
            print("✓ Browser page created")
            
            # Navigate to a test page
            await page.goto("https://example.com", timeout=10000)
            print("✓ Navigation successful")
            
            # Take a screenshot
            screenshot = await page.screenshot(type="jpeg", quality=80)
            print(f"✓ Screenshot captured ({len(screenshot)} bytes)")
            
            # Get page title
            title = await page.title()
            print(f"✓ Page title: {title}")
            
            await browser.close()
            print("✓ Browser closed cleanly")
            
        print("\n=== All Tests Passed ===")
        print("Playwright is properly configured and ready for end-to-end browser automation!")
        return True
        
    except Exception as e:
        print(f"\n✗ Playwright test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    check_environment()
    success = await test_playwright()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
