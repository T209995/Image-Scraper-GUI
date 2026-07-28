#!/usr/bin/env python3
"""
Dependencies:
    pip install requests beautifulsoup4
"""

import logging
import os
import re
import threading
import mimetypes
from urllib.parse import urljoin, urlparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ImageScraper")


def make_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retries = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "ImageScraper/1.0 (+https://github.com/)"})
    return session


def sanitize_filename(name: str) -> str:
    # Replace invalid filesystem characters and collapse whitespace
    name = re.sub(r'[:<>"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def ensure_unique_path(folder: str, filename: str) -> str:
    base, ext = os.path.splitext(filename)
    candidate = filename
    i = 1
    while os.path.exists(os.path.join(folder, candidate)):
        candidate = f"{base}_{i}{ext}"
        i += 1
    return os.path.join(folder, candidate)


def extension_from_content_type(content_type: str) -> str:
    if not content_type:
        return ""
    ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
    if ext == ".jpe":
        ext = ".jpg"
    return ext or ""


class ImageScraperGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Scraper")

        # URL entry
        ttk.Label(master, text="Enter URL:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.url_entry = ttk.Entry(master, width=60)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW, columnspan=2)

        # Folder entry + browse
        ttk.Label(master, text="Save to folder:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_entry = ttk.Entry(master, width=50)
        self.folder_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.browse_button = ttk.Button(master, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        # Buttons
        self.scrape_button = ttk.Button(master, text="Scrape Images", command=self.start_scrape)
        self.scrape_button.grid(row=2, column=1, padx=5, pady=10, sticky=tk.E)
        self.cancel_button = ttk.Button(master, text="Cancel", command=self.cancel, state="disabled")
        self.cancel_button.grid(row=2, column=2, padx=5, pady=10, sticky=tk.W)

        # Progress UI
        self.status_label = ttk.Label(master, text="")
        self.status_label.grid(row=3, column=0, columnspan=3, padx=5, pady=(0, 5), sticky=tk.W)
        self.progress = ttk.Progressbar(master, orient="horizontal", mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=5, pady=(0, 10), sticky=tk.EW)

        master.grid_columnconfigure(1, weight=1)

        # Internal state
        self._stop_event = threading.Event()
        self._thread = None

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)

    def start_scrape(self):
        url = self.url_entry.get().strip()
        save_folder = self.folder_entry.get().strip()

        if not url or not save_folder:
            messagebox.showerror("Error", "Please enter both URL and save folder.")
            return

        if not os.path.isdir(save_folder):
            try:
                os.makedirs(save_folder, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create folder: {e}")
                return

        # Prepare UI and state
        self.scrape_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self._stop_event.clear()
        self.progress["value"] = 0
        self.status_label.config(text="Starting...")

        # Start background thread
        self._thread = threading.Thread(target=self._scrape_thread, args=(url, save_folder), daemon=True)
        self._thread.start()

    def cancel(self):
        if messagebox.askyesno("Cancel", "Cancel downloading images?"):
            self._stop_event.set()
            self.status_label.config(text="Cancelling...")

    def _scrape_thread(self, url: str, save_folder: str):
        session = make_session()
        errors = []
        successes = []

        try:
            self._ui_update("Fetching page...", 0)
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
            html = resp.text

            self._ui_update("Parsing HTML...", 0)
            soup = BeautifulSoup(html, "html.parser")

            img_urls = self._extract_image_urls(soup, url)

            if not img_urls:
                self._finish_with_message("No images found on this page.", successes, errors)
                return

            total = len(img_urls)
            self._ui_update(f"Found {total} image(s). Starting downloads...", 0)
            self.master.after(0, lambda: self.progress.configure(maximum=total))

            for idx, img_url in enumerate(img_urls, start=1):
                if self._stop_event.is_set():
                    break
                try:
                    self._ui_update(f"Downloading {idx}/{total}...", idx - 1)
                    saved = self._download_image(session, img_url, save_folder)
                    successes.append(saved)
                    logger.info("Saved %s", saved)
                except Exception as exc:
                    logger.exception("Error downloading %s", img_url)
                    errors.append((img_url, str(exc)))
                finally:
                    self.master.after(0, lambda v=idx: self.progress.configure(value=v))

            # Completed or cancelled
            if self._stop_event.is_set():
                self._finish_with_message("Cancelled by user.", successes, errors)
            else:
                self._finish_with_message("Download complete!", successes, errors)

        except Exception as e:
            logger.exception("Fatal error during scrape")
            self.master.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
            self._ui_update("Error occurred.")
        finally:
            # Re-enable UI
            self.master.after(0, lambda: self.scrape_button.config(state="normal"))
            self.master.after(0, lambda: self.cancel_button.config(state="disabled"))

    def _extract_image_urls(self, soup: BeautifulSoup, base_url: str):
        found = []
        seen = set()

        for tag in soup.find_all("img"):
            src = tag.get("src") or tag.get("data-src") or ""
            # srcset handling: pick first candidate
            srcset = tag.get("srcset")
            if srcset:
                # srcset format: "url1 1x, url2 2x, ..."
                first = srcset.split(",")[0].strip().split(" ")[0]
                if first:
                    src = first

            if not src:
                continue
            # ignore data URIs
            if src.startswith("data:"):
                continue

            absolute = urljoin(base_url, src)
            if absolute not in seen:
                seen.add(absolute)
                found.append(absolute)
        return found

    def _download_image(self, session: requests.Session, img_url: str, save_folder: str) -> str:
        # Stream download to a temp file then move to final location
        resp = session.get(img_url, stream=True, timeout=15)
        resp.raise_for_status()

        # Derive filename from URL path
        parsed = urlparse(img_url)
        name = os.path.basename(parsed.path) or ""
        name = sanitize_filename(name)

        # If no filename or no extension, try Content-Type
        _, ext = os.path.splitext(name)
        if not name or not ext:
            content_type = resp.headers.get("Content-Type", "")
            ext_guess = extension_from_content_type(content_type)
            if not ext and not name:
                name = f"image"
            if not name.endswith(ext_guess):
                name = name + (ext_guess or ".jpg")

        # Ensure sanitized and unique
        name = sanitize_filename(name)
        path = ensure_unique_path(save_folder, name)

        # Write file in chunks
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=32 * 1024):
                if self._stop_event.is_set():
                    # Cleanup partial file
                    try:
                        f.close()
                        os.remove(path)
                    except Exception:
                        pass
                    raise Exception("Cancelled")
                if chunk:
                    f.write(chunk)
        return path

    def _ui_update(self, text: str, progress_value: int):
        # Schedule updates on the main thread
        self.master.after(0, lambda: self.status_label.config(text=text))
        # progress_value is handled by caller through master.after when appropriate

    def _finish_with_message(self, summary: str, successes, errors):
        def _show():
            self.status_label.config(text=summary)
            if errors:
                # Show a summary dialog with counts and offer details in logs
                messagebox.showwarning(
                    "Finished with errors",
                    f"{summary}\n\nDownloaded: {len(successes)}\nFailed: {len(errors)}\n\n"
                    "See console/log for details of failures.",
                )
            else:
                messagebox.showinfo("Success", f"{summary}\n\nDownloaded: {len(successes)}")
        self.master.after(0, _show)


def main():
    root = tk.Tk()
    app = ImageScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
