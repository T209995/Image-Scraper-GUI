import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import urllib.request
import re
import os

class ImageScraperGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Scraper")

        self.url_label = ttk.Label(master, text="Enter URL:")
        self.url_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.url_entry = ttk.Entry(master, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        self.folder_label = ttk.Label(master, text="Save to folder:")
        self.folder_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.folder_entry = ttk.Entry(master, width=40)
        self.folder_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        self.browse_button = ttk.Button(master, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        self.scrape_button = ttk.Button(master, text="Scrape Images", command=self.scrape_images)
        self.scrape_button.grid(row=2, column=1, padx=5, pady=10)

        self.status_label = ttk.Label(master, text="")
        self.status_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        master.grid_columnconfigure(1, weight=1)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, folder_path)

    def scrape_images(self):
        url = self.url_entry.get()
        save_folder = self.folder_entry.get()

        if not url or not save_folder:
            messagebox.showerror("Error", "Please enter both URL and save folder.")
            return

        try:
            self.status_label.config(text="Fetching URL...")
            self.master.update_idletasks()

            response = urllib.request.urlopen(url)
            html_content = response.read().decode('utf-8', errors='ignore')

            self.status_label.config(text="Extracting image URLs...")
            self.master.update_idletasks()

            img_tags = re.findall(r'<img.*?src=["\'](.*?)["\'].*?>', html_content)

            if not img_tags:
                messagebox.showinfo("Info", "No images found on this page.")
                self.status_label.config(text="")
                return

            self.status_label.config(text="Downloading images...")
            self.master.update_idletasks()

            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            for i, img_url in enumerate(img_tags):
                try:
                    if not img_url.startswith('http'):
                        img_url = urllib.parse.urljoin(url, img_url)

                    img_name = os.path.basename(urllib.parse.urlparse(img_url).path)
                    if not img_name:
                      img_name = f"image_{i+1}.jpg"

                    img_path = os.path.join(save_folder, img_name)

                    urllib.request.urlretrieve(img_url, img_path)

                    self.status_label.config(text=f"Downloaded: {img_name} ({i+1}/{len(img_tags)})")
                    self.master.update_idletasks()

                except Exception as e:
                    print(f"Error downloading {img_url}: {e}")

            self.status_label.config(text="Download complete!")
            messagebox.showinfo("Success", "Images downloaded successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status_label.config(text="Error occurred.")

root = tk.Tk()
gui = ImageScraperGUI(root)
root.mainloop()
