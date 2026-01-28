# Invoice System (Offline)

A lightweight, portable invoice management system that works **offline**. It includes **VAT support** and **ZATCA-compliant QR** generation for Saudi Arabia.

## ✨ Features

- Create invoices (Arabic + English UI)
- Automatic VAT calculation (default 15% via settings)
- ZATCA QR code generation
- Professional PDF export/printing
- Invoice history with search and date filtering
- Export history:
  - CSV (Excel-friendly)
  - Batch PDF export (one PDF per invoice)
- Database backups and restore
- Works fully offline (SQLite)

## 🌐 Language

Use the top menubar: **Language → English / Arabic**.

The selected language switches instantly and is remembered next time you open the app.

## 💻 System Requirements

- Windows 7/10/11
- Python 3.8+ (recommended)
- ~100MB disk space

## 🚀 Installation

### 1) Install Python

Download Python from [python.org](https://www.python.org/downloads/) and enable **“Add Python to PATH”** during installation.

### 2) (Recommended) Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3) Install dependencies

```powershell
cd "path\to\InvoiceApp"
pip install -r requirements.txt
```

### 4) Run

```powershell
python main.py
```

## 🧭 Usage

### Create a new invoice

- Open the app (Home tab)
- Enter customer info (optional)
- Add items, qty, and price
- Click **Save** or **Save & Print**

### View invoice history

- Go to **History**
- Search by invoice number or customer
- Use date filters
- Double-click an invoice to open it

### Export history (CSV / PDF)

- Go to **History**
- Select invoices
- Export:
  - **CSV**: one file (Excel-friendly; English headers when UI is English)
  - **PDF**: one PDF per invoice to a selected folder

### Company settings

- Go to **Settings**
- Update company info, VAT rate, invoice numbering, and terms
- Save settings

## 🛡️ Backup & Restore

- **Create backup**: Settings → Create backup
- **Restore backup**: Settings → Restore backup

## 📦 Build a Windows `.exe` (PyInstaller)

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name="InvoiceApp" --icon=assets/icon.ico main.py
```

Output: `dist/InvoiceApp.exe`

If you don’t have an icon file, remove `--icon=assets/icon.ico`.

## 🔤 Arabic PDF font support

For best Arabic rendering in generated PDFs, place an Arabic `.ttf` font in `assets/fonts/` (e.g. **Amiri** or **Cairo**) and restart the app.

## 📁 Project Structure

```
InvoiceApp/
├── main.py
├── requirements.txt
├── README.md
├── app/
│   ├── database.py
│   ├── exporter.py
│   ├── invoice_logic.py
│   ├── pdf_generator.py
│   ├── qr_generator.py
│   └── i18n.py
├── ui/
│   ├── main_window.py
│   ├── invoice_form.py
│   ├── invoice_history.py
│   ├── invoice_view.py
│   ├── settings.py
│   ├── export_dialog.py
│   └── widgets.py
├── data/       # invoices.db is created automatically
├── output/     # generated PDFs
└── backups/    # backup files
```

## License

This project is available for personal and commercial use.

---

Developed by: Contributors  \nDate: January 2026
