# Smart Global Trading – Quotation Web App

A professional quotation generator that works on **any device** — phone, tablet, desktop.

---

## 🚀 Deploy to Railway (FREE – Recommended)

1. Create a free account at **https://railway.app**
2. Click **"New Project"** → **"Deploy from GitHub"**
3. Upload this folder to a GitHub repo first (or use Railway's direct upload)
4. Railway auto-detects Flask and deploys it
5. You get a URL like `https://your-app.railway.app` — open it on any phone!

---

## 🚀 Deploy to Render (FREE alternative)

1. Create a free account at **https://render.com**
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repo containing these files
4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click Deploy — done!

---

## 💻 Run Locally (on your computer)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open **http://localhost:5000** in your browser.  
On the same WiFi, open **http://YOUR_COMPUTER_IP:5000** on your phone.

---

## 📁 Files

| File | Purpose |
|------|---------|
| `app.py` | Flask backend + PDF generation |
| `templates/index.html` | Beautiful web UI |
| `items.csv` | Default product catalog |
| `smart_logo.jpg` | Company logo |
| `requirements.txt` | Python dependencies |
| `Procfile` | Cloud deployment config |

---

## 📦 Updating Your Product Catalog

Edit `items.csv` with your real products. Columns:
- **Item Name** — product name (shown in dropdown)
- **Description** — optional details
- **Unit Price (USD)** — base price
- **Unit** — Piece, Set, Box, etc.

Or upload any CSV/Excel directly in the app using the **"Upload Price List"** button.

---

## Features

- ✅ Works on Android, iPhone, tablet, desktop
- ✅ Dropdown autocomplete from your price list
- ✅ Auto-calculates VAT 16%
- ✅ Generates professional PDF with your logo
- ✅ Upload CSV/Excel price lists on the fly
- ✅ Multiple currencies (USD, EUR, GBP, KES)
