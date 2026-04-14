"""
Browser Launcher v4.4.1 - Camoufox Edition
Fixed: Removed strict Screen/Locale constraints to completely prevent 
BrowserForge dataset crashes ("No headers based on this input" error).
"""

import sys
import os
import io
import asyncio
import ctypes
import tempfile
import random
import subprocess
from PIL import Image
from pathlib import Path
from fingerprint_engine import load_fingerprint

# -- FIX FOR PYINSTALLER WINDOWED MODE --
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

# Force UTF-8 encoding for stdout to prevent terminal crashes on Windows
try:
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

def get_physical_screen():
    """Detect the actual physical screen size of the user's machine to prevent overflow."""
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        # Subtract margins to leave room for the Windows taskbar and window borders
        return (width - 20, height - 80)
    except Exception:
        # Safe fallback if ctypes fails
        return (1366, 768)

async def launch_browser(profile_name: str,
                         url: str = "about:newtab",
                         profiles_dir: str = "profiles",
                         headless: bool = False):
    from camoufox.async_api import AsyncCamoufox

    fp = load_fingerprint(profile_name, profiles_dir)
    user_data_dir = os.path.join(profiles_dir, f"browser_data_{profile_name}")
    Path(user_data_dir).mkdir(exist_ok=True)

    # -- TAB DOUBLE-CLICK FIX (Zero-Bug Method) -----------------------------
    try:
        prefs_file = os.path.join(user_data_dir, "user.js")
        with open(prefs_file, "w") as f:
            f.write('user_pref("browser.tabs.drawInTitlebar", false);\n')
            f.write('user_pref("browser.tabs.inTitlebar", 0);\n')
            f.write('user_pref("dom.w3c_touch_events.enabled", 0);\n')
    except Exception:
        pass

    # -- Format Proxy for Playwright/Camoufox -------------------------------
    proxy_config = None
    proxy_data = fp.get("proxy")
    if proxy_data and proxy_data.get("host"):
        proxy_config = {
            "server": f"{proxy_data.get('protocol', 'http')}://{proxy_data['host']}:{proxy_data['port']}"
        }
        if proxy_data.get("username"):
            proxy_config["username"] = proxy_data["username"]
            proxy_config["password"] = proxy_data.get("password", "")

    # -- Resolution Setup ---------------------------------------------------
    # Pull the safe resolution from the database instead of measuring the laptop
    safe_width = fp.get("screen_width", 1920)
    safe_height = fp.get("screen_height", 1080)

    print(f"\n[{profile_name}] -- Launching ------------------------------")
    print(f"  Engine:   Camoufox (Native binary-level fingerprinting)")
    print(f"  OS:       {fp.get('os_name', 'Windows')}")
    print(f"  Screen:   {safe_width}x{safe_height} (Safe Anti-Detect Resolution)")
    
    if proxy_config:
        print(f"  Proxy:    {proxy_config['server']}")
    else:
        print(f"  Proxy:    None (VPN mode or local)")

    # Map to host machine's actual Downloads folder (Forced forward slashes for Firefox JSON)
    host_downloads = os.path.join(os.path.expanduser("~"), "Downloads").replace("\\", "/")

    # -- Build Camoufox launch kwargs ---------------------------------------
    launch_kwargs = dict(
        headless=headless,
        persistent_context=True,
        user_data_dir=user_data_dir,
        os=fp.get("os_name", "windows").lower(),
        locale="en-US",
        block_webrtc=True,
        timezone_id=fp.get("timezone", "America/New_York"),
        
        window=(safe_width, safe_height),
        viewport={"width": safe_width, "height": safe_height},
        
        # Enforce boring, normal hardware to prevent 32-core workstation anomalies
        config={
            "navigator.hardwareConcurrency": 8
        },
        
        # DPI Bypass & Host Downloads Routing
        firefox_user_prefs={
            "layout.css.devPixelsPerPx": "1.0",
            "browser.download.folderList": 2,
            "browser.download.dir": host_downloads,
            "browser.download.useDownloadDir": True
        },
        
        humanize=True, 
        i_know_what_im_doing=True,
    )

    if proxy_config:
        launch_kwargs["proxy"] = proxy_config

    launch_kwargs["enable_cache"] = True

    # -- Silent Upload Interceptor Logic (Crash-Proof Process Isolation) --
    def get_files_via_dialog(is_multiple):
        # Runs tkinter in a completely separate isolated process
        # This prevents the fatal C-level thread crash with PyQt6 and Asyncio
        script = f"""
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.attributes('-topmost', True)
root.withdraw()
if {is_multiple}:
    files = filedialog.askopenfilenames(title="Ninja Shield - Select Images")
    print("|".join(files))
else:
    file = filedialog.askopenfilename(title="Ninja Shield - Select Image")
    print(file)
"""
        try:
            import sys
            kwargs = {}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                
            result = subprocess.run(["python", "-c", script], capture_output=True, text=True, **kwargs)
            paths = result.stdout.strip().split("|")
            return [p for p in paths if p]
        except Exception:
            return []

    async def handle_filechooser(file_chooser):
        print("  [Ninja Shield] Intercepting file upload...")
        loop = asyncio.get_running_loop()
        file_paths = await loop.run_in_executor(None, get_files_via_dialog, file_chooser.is_multiple)

        if not file_paths:
            await file_chooser.set_files([])
            return

        clean_paths = []
        temp_dir = tempfile.gettempdir()

        for path in file_paths:
            try:
                # 1. Open and standardize image
                img = Image.open(path)
                if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
                
                # 2. Strip EXIF by dumping raw pixels to a new canvas
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(list(img.getdata()))

                # 3. Hash Obliteration (Alter exactly 1 pixel slightly)
                pixels = clean_img.load()
                x, y = random.randint(0, img.width-1), random.randint(0, img.height-1)
                r, g, b = pixels[x, y]
                pixels[x, y] = (max(0, r-1), g, b)

                # 4. Save to hidden temp folder
                base = os.path.basename(path)
                name, ext = os.path.splitext(base)
                temp_path = os.path.join(temp_dir, f"ns_clean_{random.randint(1000,9999)}.jpg")
                clean_img.save(temp_path, "JPEG", quality=random.randint(92, 97))
                clean_paths.append(temp_path)
                print(f"  [Ninja Shield] Scrubbed and rebuilt hash for: {base}")
            except Exception as e:
                print(f"  [WARN] Failed to clean image: {e}. Uploading original.")
                clean_paths.append(path)

        # Inject the scrubbed files into the Facebook webpage
        await file_chooser.set_files(clean_paths)

    # --- Try to launch browser ---------------------------------------------
    print(f"  Launching Camoufox...")
    try:
        async with AsyncCamoufox(**launch_kwargs) as browser:
            print(f"  Browser instance created.")
            
            # Get persistent page or open a new one
            try:
                page = browser.pages[0] if browser.pages else await browser.new_page()
                
                # Activate the Silent File Interceptor
                page.on("filechooser", lambda fc: asyncio.create_task(handle_filechooser(fc)))
                
                print(f"  Page opened. Upload Interceptor Active.")
            except Exception as e:
                print(f"  ERROR: Could not get/create page: {e}")
                raise

            # Navigate to URL
            try:
                if url != "about:blank" and url != "about:newtab":
                    await page.goto(url, wait_until="commit", timeout=30000)
                    print(f"  Navigated to {url}.")
            except Exception as e:
                print(f"  [WARN] Navigation error: {e} (ignored)")

            print(f"\n[{profile_name}]  Browser ready!")
            print(f"  Close the browser window to exit.\n")

            # Keep-alive loop — signals GUI when browser closes
            disconnected = asyncio.Event()
            browser.on("disconnected", lambda: disconnected.set())
            try:
                await asyncio.wait_for(disconnected.wait(), timeout=None)
            except (asyncio.TimeoutError, KeyboardInterrupt, asyncio.CancelledError):
                pass
            finally:
                try:
                    await browser.close()
                except Exception:
                    pass
                print(f"[{profile_name}] Browser closed.")

    except Exception as e:
        import traceback
        print(f"[{profile_name}] FATAL: Launch failed: {e}")
        traceback.print_exc()
        raise

def launch_profile(profile_name: str,
                   url: str = "about:newtab",
                   profiles_dir: str = "profiles"):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(launch_browser(profile_name, url=url, profiles_dir=profiles_dir))


if __name__ == "__main__":
    profile = sys.argv[1] if len(sys.argv) > 1 else "profile_1"
    profiles_dir = sys.argv[2] if len(sys.argv) > 2 else "profiles"
    launch_profile(profile, profiles_dir=profiles_dir)