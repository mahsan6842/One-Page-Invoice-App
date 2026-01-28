# مشروع تطبيق الفواتير - Invoice Application Plan

## 📋 Invoice Analysis (Based on Uploaded Image)

### Invoice Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│  HEADER: Company Name (Arabic) + Logo Area                  │
│  مؤسسة التفرد الاصيل للمطابخ                                │
│  Address: بريدة - طريق الملك فيصل - حي العجيبة              │
│  Tax Number: 300694858900003                                │
│  Contact: 0591650315 - 0580911269                           │
├─────────────────────────────────────────────────────────────┤
│  INVOICE INFO BOX                                           │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ فاتورة مبيعات   │  │ Invoice #       │                   │
│  │ Sales Invoice   │  │ 2024100127      │                   │
│  │                 │  │ Date: 06/03/2025│                   │
│  │                 │  │ Payment: نقدا   │                   │
│  │                 │  │ Saler: admin    │                   │
│  └─────────────────┘  └─────────────────┘                   │
├─────────────────────────────────────────────────────────────┤
│  CUSTOMER INFO                                              │
│  Customer: فهد عبد المطيري    Tax Number: 0544054759        │
│  Address: ________________    Phone: _______________        │
├─────────────────────────────────────────────────────────────┤
│  ITEMS TABLE (RTL - Right to Left)                          │
│  ┌──────┬───────┬──────┬─────┬───────┬────────┬─────┬─────┐ │
│  │الصافي│الضريبة│الخصم │الاجمالي│السعر │الكمية│الوحدة│الصنف│ │
│  │ NET  │ TAX   │Disc. │Total │Price │ QTY  │Unit │Items│ │
│  ├──────┼───────┼──────┼─────┼───────┼────────┼─────┼─────┤ │
│  │7000.05│913.05│ 0%   │6087 │6087   │  1   │ حبة │مطبخ │ │
│  └──────┴───────┴──────┴─────┴───────┴────────┴─────┴─────┘ │
├─────────────────────────────────────────────────────────────┤
│  TOTALS & QR CODE                                           │
│  ┌─────────────────────┐    ┌─────────────┐                 │
│  │ Discount:    0.00   │    │             │                 │
│  │ Taxable:  6,087.00  │    │   QR CODE   │                 │
│  │ TAX 15%:    913.05  │    │   (ZATCA)   │                 │
│  │ Net:      7,000.05  │    │             │                 │
│  └─────────────────────┘    └─────────────┘                 │
├─────────────────────────────────────────────────────────────┤
│  TERMS & CONDITIONS (8 Arabic terms)                        │
│  1- يدفع الزبون 50% من قيمة الفاتورة...                     │
│  2- عند انتهاء المحلات من التصنيع...                        │
│  ...                                                        │
├─────────────────────────────────────────────────────────────┤
│  SIGNATURE: توقيع العميل .........                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Recommended Tech Stack

### Language: **Python 3.10+**
**Justification:**
- ✅ Beginner-friendly syntax, easy to learn
- ✅ Excellent Arabic/RTL support with libraries
- ✅ Built-in `tkinter` for GUI (no extra installation)
- ✅ Built-in `sqlite3` for database (lightweight, offline)
- ✅ Low memory footprint, runs on old hardware
- ✅ Can be packaged as single `.exe` file

### GUI Framework: **Tkinter + ttk**
**Justification:**
- ✅ Comes with Python (no extra installation)
- ✅ Native Windows look and feel
- ✅ Very lightweight (~5MB RAM usage)
- ✅ Simple learning curve for beginners
- ✅ Supports Arabic text input

### Database: **SQLite**
**Justification:**
- ✅ Single file database (easy backup - just copy the file)
- ✅ Zero configuration, no server needed
- ✅ Built into Python (no installation)
- ✅ Handles 100,000+ invoices easily
- ✅ Perfect for offline, single-user applications

### PDF Generation: **ReportLab**
**Justification:**
- ✅ Industry standard for Python PDF generation
- ✅ Full control over layout positioning
- ✅ Supports custom fonts (Arabic TTF)
- ✅ Can embed images (QR codes, logos)
- ✅ Lightweight and fast

### Arabic Text Support
- **arabic-reshaper**: Reshapes Arabic letters for correct display
- **python-bidi**: Handles Right-to-Left text direction

### QR Code: **qrcode + Pillow**
- Generates ZATCA-compliant QR codes
- Base64 TLV encoding for Saudi e-invoicing

---

## 🏗️ Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Create      │  │ Invoice     │  │ View/Print          │  │
│  │ Invoice     │  │ History     │  │ Invoice             │  │
│  │ Screen      │  │ Screen      │  │ Screen              │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
├─────────┼────────────────┼─────────────────────┼─────────────┤
│         └────────────────┼─────────────────────┘             │
│                          ▼                                   │
│                  BUSINESS LOGIC LAYER                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  • Invoice Number Generator (Auto-increment)            │ │
│  │  • VAT Calculator (15% Saudi standard)                  │ │
│  │  • Discount Calculator                                  │ │
│  │  • Input Validation                                     │ │
│  │  • QR Code Generator (ZATCA TLV format)                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                   │
├──────────────────────────┼───────────────────────────────────┤
│                          ▼                                   │
│                    DATA LAYER                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              SQLite Database                            │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │ │
│  │  │ Company  │ │Customers │ │ Invoices │ │Invoice     │ │ │
│  │  │ Settings │ │          │ │          │ │Items       │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                   │
├──────────────────────────┼───────────────────────────────────┤
│                          ▼                                   │
│                   OUTPUT LAYER                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  PDF Generator (ReportLab)                              │ │
│  │  • Arabic font embedding                                │ │
│  │  • QR code embedding                                    │ │
│  │  • Print to Windows default printer                     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### Table: `company_settings`
```sql
CREATE TABLE company_settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    company_name_ar TEXT NOT NULL,        -- مؤسسة التفرد الاصيل للمطابخ
    company_name_en TEXT,                  -- Al-Tafarud Al-Aseel Kitchen
    address_ar TEXT,                       -- بريدة - طريق الملك فيصل
    address_en TEXT,
    tax_number TEXT NOT NULL,              -- 300694858900003
    phone1 TEXT,                           -- 0591650315
    phone2 TEXT,                           -- 0580911269
    logo_path TEXT,                        -- Path to company logo
    vat_rate REAL DEFAULT 0.15,            -- 15% VAT
    terms_conditions TEXT,                 -- JSON array of terms
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `customers`
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ar TEXT NOT NULL,                 -- فهد عبد المطيري
    name_en TEXT,
    tax_number TEXT,                       -- 0544054759
    phone TEXT,
    address TEXT,
    email TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `invoices`
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,   -- 2024100127
    invoice_date DATE NOT NULL,            -- 2025-03-06
    invoice_time TIME,                     -- 05:37:56
    customer_id INTEGER,
    customer_name TEXT,                    -- For quick access
    customer_tax_number TEXT,
    customer_phone TEXT,
    customer_address TEXT,
    payment_type TEXT DEFAULT 'cash',      -- cash, credit, bank_transfer
    salesperson TEXT DEFAULT 'admin',
    subtotal REAL NOT NULL,                -- 6087.00
    discount_percent REAL DEFAULT 0,       -- 0%
    discount_amount REAL DEFAULT 0,        -- 0.00
    taxable_amount REAL NOT NULL,          -- 6087.00
    tax_amount REAL NOT NULL,              -- 913.05
    net_total REAL NOT NULL,               -- 7000.05
    notes TEXT,
    status TEXT DEFAULT 'active',          -- active, cancelled, refunded
    qr_code_data TEXT,                     -- Base64 encoded QR data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

### Table: `invoice_items`
```sql
CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,               -- مطبخ تفصيل المنيوم
    item_barcode TEXT,
    unit TEXT DEFAULT 'حبة',               -- حبة, متر, كيلو
    quantity REAL NOT NULL,                -- 1
    unit_price REAL NOT NULL,              -- 6087.00
    total_price REAL NOT NULL,             -- 6087.00
    discount_percent REAL DEFAULT 0,
    discount_amount REAL DEFAULT 0,
    tax_amount REAL NOT NULL,              -- 913.05
    net_amount REAL NOT NULL,              -- 7000.05
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
);
```

### Table: `products` (Optional - for autocomplete)
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    name_ar TEXT NOT NULL,
    name_en TEXT,
    unit TEXT DEFAULT 'حبة',
    default_price REAL,
    category TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes for Performance
```sql
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_customer ON invoices(customer_id);
CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX idx_customers_name ON customers(name_ar);
```

---

## 📄 PDF Generation Strategy

### Layout Specifications (A4 Paper: 595 x 842 points)

```
PDF LAYOUT COORDINATES (points from bottom-left)
┌─────────────────────────────────────────┐ 842
│  MARGINS: 40pt all sides                │
│  ┌─────────────────────────────────────┐│ 802
│  │ HEADER ZONE (y: 720-802)            ││
│  │ Company name, logo, contact info    ││
│  ├─────────────────────────────────────┤│ 720
│  │ INVOICE INFO ZONE (y: 650-720)      ││
│  │ Invoice number, date, payment type  ││
│  ├─────────────────────────────────────┤│ 650
│  │ CUSTOMER ZONE (y: 580-650)          ││
│  │ Customer name, tax number, phone    ││
│  ├─────────────────────────────────────┤│ 580
│  │ ITEMS TABLE ZONE (y: 300-580)       ││
│  │ Dynamic height based on items count ││
│  ├─────────────────────────────────────┤│ 300
│  │ TOTALS + QR ZONE (y: 180-300)       ││
│  │ Left: Totals box, Right: QR code    ││
│  ├─────────────────────────────────────┤│ 180
│  │ TERMS ZONE (y: 60-180)              ││
│  │ Terms & conditions list             ││
│  ├─────────────────────────────────────┤│ 60
│  │ SIGNATURE ZONE (y: 40-60)           ││
│  └─────────────────────────────────────┘│ 40
└─────────────────────────────────────────┘ 0
       40                              555
```

### Arabic Text Rendering Flow
```
1. Original Text: "مطبخ تفصيل المنيوم"
                    ↓
2. arabic_reshaper.reshape() → Connects letters properly
                    ↓
3. bidi.algorithm.get_display() → Reverses for RTL display
                    ↓
4. ReportLab draws with Arabic TTF font
```

### QR Code Generation (ZATCA TLV Format)
```python
# Tag-Length-Value encoding for Saudi e-invoicing
TLV_TAGS = {
    1: "Seller Name",      # مؤسسة التفرد الاصيل للمطابخ
    2: "VAT Number",       # 300694858900003
    3: "Timestamp",        # 2025-03-06T05:37:56Z
    4: "Total with VAT",   # 7000.05
    5: "VAT Amount"        # 913.05
}
# Encode to Base64 → Generate QR Code Image
```

---

## 🖥️ UI Screens Breakdown

### Screen 1: Create Invoice (الرئيسية)
```
┌──────────────────────────────────────────────────────────────┐
│  [🏠 الرئيسية]  [📋 السجل]  [⚙️ الإعدادات]                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ معلومات العميل ─────────────────────────────────────────┐│
│  │ اسم العميل: [_______________▼]  الرقم الضريبي: [_______] ││
│  │ الهاتف:     [_______________]   العنوان:      [_______] ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌─ الأصناف ────────────────────────────────────────────────┐│
│  │ ┌──────────────────────────────────────────────────────┐ ││
│  │ │الصنف          │الوحدة│الكمية│السعر  │الإجمالي│ حذف  │ ││
│  │ ├──────────────────────────────────────────────────────┤ ││
│  │ │[____________] │[حبة▼]│[ 1  ]│[     ]│ 0.00   │ [🗑️] │ ││
│  │ │[____________] │[حبة▼]│[ 1  ]│[     ]│ 0.00   │ [🗑️] │ ││
│  │ └──────────────────────────────────────────────────────┘ ││
│  │                                      [+ إضافة صنف]       ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌─ الإجماليات ─────────────────────────────────────────────┐│
│  │  المجموع:          0.00 ريال                             ││
│  │  الخصم (%):    [0 ] → 0.00 ريال                          ││
│  │  ─────────────────────────                               ││
│  │  الخاضع للضريبة:   0.00 ريال                             ││
│  │  ضريبة 15%:        0.00 ريال                             ││
│  │  ═════════════════════════                               ││
│  │  الصافي شامل الضريبة: 0.00 ريال                          ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  نوع الدفع: (●) نقدا  ( ) آجل  ( ) تحويل بنكي                │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  💾 حفظ      │  │  🖨️ حفظ وطباعة│  │  ❌ إلغاء    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└──────────────────────────────────────────────────────────────┘
```

### Screen 2: Invoice History (سجل الفواتير)
```
┌──────────────────────────────────────────────────────────────┐
│  [🏠 الرئيسية]  [📋 السجل]  [⚙️ الإعدادات]                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  🔍 بحث: [_______________]  من: [📅____] إلى: [📅____]       │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ رقم الفاتورة │ التاريخ    │ العميل        │ الإجمالي │    ││
│  ├──────────────────────────────────────────────────────────┤│
│  │ 2024100127   │ 2025-03-06 │ فهد عبد المطيري│ 7,000.05│ 👁️ ││
│  │ 2024100126   │ 2025-03-05 │ أحمد محمد     │ 3,500.00│ 👁️ ││
│  │ 2024100125   │ 2025-03-04 │ سعد العتيبي   │ 12,650.00│ 👁️││
│  │ ...          │ ...        │ ...           │ ...     │    ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  إجمالي الفواتير: 127  │  إجمالي المبيعات: 450,000.00 ريال   │
│                                                              │
│  [📤 تصدير Excel]  [📊 تقرير يومي]                           │
└──────────────────────────────────────────────────────────────┘
```

### Screen 3: View/Print Invoice (عرض الفاتورة)
```
┌──────────────────────────────────────────────────────────────┐
│  فاتورة رقم: 2024100127                      [✖️ إغلاق]      │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐│
│  │                                                          ││
│  │              [ PDF PREVIEW AREA ]                        ││
│  │                                                          ││
│  │         Embedded PDF or Image Preview                    ││
│  │                                                          ││
│  │                                                          ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  🖨️ طباعة    │  │  💾 حفظ PDF  │  │  📧 إرسال    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└──────────────────────────────────────────────────────────────┘
```

### Screen 4: Settings (الإعدادات)
```
┌──────────────────────────────────────────────────────────────┐
│  [🏠 الرئيسية]  [📋 السجل]  [⚙️ الإعدادات]                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ بيانات المؤسسة ─────────────────────────────────────────┐│
│  │ اسم المؤسسة:     [مؤسسة التفرد الاصيل للمطابخ_________] ││
│  │ الرقم الضريبي:   [300694858900003____________________] ││
│  │ العنوان:         [بريدة - طريق الملك فيصل_____________] ││
│  │ الهاتف 1:        [0591650315_________________________] ││
│  │ الهاتف 2:        [0580911269_________________________] ││
│  │ الشعار:          [اختيار صورة...]                       ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌─ إعدادات الفاتورة ───────────────────────────────────────┐│
│  │ نسبة الضريبة:    [15] %                                  ││
│  │ بادئة رقم الفاتورة: [2024]                               ││
│  │ الرقم التالي:    [100128]                                ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌─ الشروط والأحكام ────────────────────────────────────────┐│
│  │ [________________________________________________]       ││
│  │ [________________________________________________]       ││
│  │ [+ إضافة شرط]                                            ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                          │
│  │  💾 حفظ      │  │  🔄 استعادة   │                          │
│  └──────────────┘  └──────────────┘                          │
└──────────────────────────────────────────────────────────────┘
```

---

## 📅 Step-by-Step Implementation Roadmap

### Phase 1: Foundation (Week 1)
| Day | Task | Details |
|-----|------|---------|
| 1 | Install Python | Download Python 3.10 from python.org, add to PATH |
| 1 | Setup Project | Create folder structure, virtual environment |
| 2 | Install Libraries | `pip install reportlab arabic-reshaper python-bidi qrcode pillow` |
| 2 | Download Arabic Font | Get "Amiri" or "Cairo" TTF font |
| 3 | Create Database | Write `database.py` with SQLite schema |
| 3 | Test Database | Insert and retrieve sample data |
| 4-5 | Basic UI Window | Create main Tkinter window with navigation |

### Phase 2: Core Features (Week 2)
| Day | Task | Details |
|-----|------|---------|
| 1-2 | Invoice Form UI | Build Create Invoice screen with all fields |
| 3 | Business Logic | Invoice number generator, VAT calculator |
| 4 | Save Invoice | Connect form to database |
| 5 | Invoice History | List screen with search functionality |

### Phase 3: PDF Generation (Week 3)
| Day | Task | Details |
|-----|------|---------|
| 1-2 | PDF Layout | Create basic PDF structure matching invoice |
| 3 | Arabic Text | Integrate reshaper and bidi for RTL |
| 4 | QR Code | Generate ZATCA-compliant QR codes |
| 5 | Print Function | Windows printing integration |

### Phase 4: Polish & Package (Week 4)
| Day | Task | Details |
|-----|------|---------|
| 1-2 | Settings Screen | Company info, terms configuration |
| 3 | Error Handling | Input validation, user messages |
| 4 | Testing | Test all features on low-spec PC |
| 5 | Build EXE | Package with PyInstaller |

---

## ⚡ Performance Considerations for Low-End Hardware

### Memory Optimization
```python
# ❌ BAD: Loading all invoices at once
invoices = db.get_all_invoices()  # Could be 10,000+ records

# ✅ GOOD: Pagination
invoices = db.get_invoices(page=1, per_page=50)
```

### Database Optimization
```python
# Use indexes for frequently searched columns
# Limit query results
# Use prepared statements (SQLite parameterized queries)

# Example: Efficient search
cursor.execute("""
    SELECT * FROM invoices 
    WHERE invoice_date BETWEEN ? AND ?
    ORDER BY id DESC
    LIMIT 100
""", (start_date, end_date))
```

### UI Responsiveness
```python
# Use threading for heavy operations
import threading

def generate_pdf_async():
    thread = threading.Thread(target=generate_pdf)
    thread.start()
    # Show progress indicator
```

### Startup Time
- Lazy load modules (import when needed)
- Pre-compile Python files (.pyc)
- Keep database file small with regular cleanup

### Minimum System Requirements
| Component | Requirement |
|-----------|-------------|
| Processor | Intel Core i3 2nd Gen (or equivalent) |
| RAM | 2 GB minimum, 4 GB recommended |
| Storage | 100 MB for app + database growth |
| OS | Windows 7/10/11 |
| Display | 1024x768 minimum |

---

## 🚀 Optional Future Enhancements

### 1. Data Export
```python
# Export to Excel
import csv
def export_to_csv(invoices, filename):
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Invoice #', 'Date', 'Customer', 'Total'])
        for inv in invoices:
            writer.writerow([inv.number, inv.date, inv.customer, inv.total])
```

### 2. Automatic Backup
```python
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy('invoices.db', f'backups/invoices_{timestamp}.db')
```

### 3. Build Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build single .exe file
pyinstaller --onefile --windowed --icon=icon.ico --name="InvoiceApp" main.py

# Output: dist/InvoiceApp.exe
```

### 4. Additional Features Roadmap
| Priority | Feature | Effort |
|----------|---------|--------|
| High | Customer autocomplete | 2 hours |
| High | Invoice duplication | 1 hour |
| Medium | Daily/Monthly reports | 4 hours |
| Medium | Product catalog | 4 hours |
| Low | Multi-language UI | 8 hours |
| Low | Barcode scanner support | 4 hours |
| Low | Email invoice (SMTP) | 4 hours |
| Low | Cloud backup (optional) | 8 hours |

---

## 📁 Project File Structure

```
InvoiceApp/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # User documentation
│
├── app/
│   ├── __init__.py
│   ├── database.py        # SQLite database operations
│   ├── models.py          # Data classes/models
│   ├── invoice_logic.py   # Business logic (VAT, numbering)
│   ├── pdf_generator.py   # PDF creation with ReportLab
│   └── qr_generator.py    # ZATCA QR code generation
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── invoice_form.py    # Create/Edit invoice screen
│   ├── invoice_history.py # Invoice list screen
│   ├── invoice_view.py    # View/Print invoice screen
│   ├── settings.py        # Settings screen
│   └── widgets.py         # Custom Tkinter widgets
│
├── assets/
│   ├── fonts/
│   │   └── Amiri-Regular.ttf    # Arabic font
│   ├── images/
│   │   └── logo.png             # Company logo
│   └── icon.ico                 # Application icon
│
├── data/
│   └── invoices.db        # SQLite database file
│
├── output/
│   └── (generated PDFs)   # PDF output folder
│
└── backups/
    └── (database backups) # Backup files
```

---

## ✅ Quick Start Commands

```bash
# 1. Create project folder
mkdir InvoiceApp
cd InvoiceApp

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install reportlab arabic-reshaper python-bidi qrcode pillow

# 4. Run the application
python main.py

# 5. Build executable (when ready)
pip install pyinstaller
pyinstaller --onefile --windowed --name="FaturaApp" main.py
```

---

## 📞 Support Checklist

Before deployment, verify:
- [ ] Application starts without errors
- [ ] Can create new invoice
- [ ] Can save invoice to database
- [ ] PDF generates with correct Arabic text
- [ ] QR code is readable
- [ ] Can print invoice
- [ ] Invoice history loads correctly
- [ ] Settings save and persist
- [ ] Works on target low-spec PC
- [ ] Executable runs without Python installed

---

*Document created: January 28, 2026*
*Target completion: 4 weeks*
*Difficulty level: Beginner-friendly*
