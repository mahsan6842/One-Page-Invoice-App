# History Export Feature - Implementation Plan

## 📋 Feature Overview

Add the ability to export invoice history to CSV/Excel or individual PDF files, working completely offline on low-spec hardware.

---

## 🎯 Requirements Summary

### CSV/Excel Export
- Single file containing all selected invoices
- Opens correctly in Excel as one sheet
- Columns: Invoice No, Date, Customer, Subtotal, Tax, Total, Payment Type
- UTF-8 with BOM for Arabic support in Excel

### PDF Export
- Each invoice = separate PDF file
- Follows original invoice layout
- Saved to user-selected folder
- Meaningful filenames: `Invoice_2024100127.pdf`

### Technical Constraints
- ✅ Works offline
- ✅ No UI freezing (background processing)
- ✅ Low memory footprint
- ✅ Beginner-friendly code

---

## 🛠️ Recommended Libraries

| Purpose | Library | Why |
|---------|---------|-----|
| CSV Export | `csv` (built-in) | No dependencies, fast, simple |
| Excel Support | UTF-8 BOM encoding | Excel reads CSV with BOM correctly |
| PDF Export | `reportlab` (already installed) | Already in project |
| Background Tasks | `threading` (built-in) | Prevents UI freeze |
| File Dialogs | `tkinter.filedialog` (built-in) | Native OS dialogs |

**No new dependencies required!**

---

## 🔄 Export Flow Logic

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. SELECT INVOICES                                              │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ ☑ Invoice 2024100127 - 2025-03-06 - فهد - 7,000.05     │ │
│     │ ☑ Invoice 2024100126 - 2025-03-05 - أحمد - 3,500.00    │ │
│     │ ☐ Invoice 2024100125 - 2025-03-04 - سعد - 12,650.00    │ │
│     └─────────────────────────────────────────────────────────┘ │
│                                                                  │
│  2. CHOOSE ACTION                                                │
│     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│     │ ☑ تحديد الكل │  │ 📊 تصدير CSV │  │ 📄 تصدير PDF │        │
│     └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✓ Check: Are any invoices selected?                            │
│    └─ If NO → Show error: "يرجى اختيار فاتورة واحدة على الأقل"  │
│                                                                  │
│  ✓ Check: Is export format chosen?                              │
│    └─ CSV or PDF                                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DESTINATION SELECTION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CSV Export:                                                     │
│    └─ Show "Save As" dialog → Single .csv file                  │
│       Default name: invoices_export_20260128.csv                │
│                                                                  │
│  PDF Export:                                                     │
│    └─ Show "Select Folder" dialog → Directory for multiple PDFs │
│       Files will be: Invoice_2024100127.pdf, etc.               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 BACKGROUND PROCESSING                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐                                                │
│  │ Main Thread │ ──→ Shows Progress Dialog                      │
│  └─────────────┘     "جاري التصدير... 3/10"                     │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │ Worker Thread │ ──→ Processes exports in background          │
│  └──────────────┘                                               │
│         │                                                        │
│         ├─── CSV: Write all rows to single file                 │
│         │                                                        │
│         └─── PDF: Generate each invoice PDF sequentially        │
│              └─ Update progress after each file                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLETION                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Success:                                                        │
│    ├─ Show success message with file count                      │
│    ├─ Option to "Open Folder" containing exported files         │
│    └─ Update status bar                                          │
│                                                                  │
│  Failure:                                                        │
│    ├─ Show specific error message                               │
│    ├─ Log error details                                          │
│    └─ Allow retry                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Error Handling Strategy

### Error Types & Responses

| Error | Detection | User Message | Recovery |
|-------|-----------|--------------|----------|
| No selection | `len(selected) == 0` | "يرجى اختيار فاتورة واحدة على الأقل" | Return to selection |
| Permission denied | `PermissionError` | "لا يمكن الكتابة في هذا المجلد. اختر مجلداً آخر" | Re-show folder dialog |
| Disk full | `OSError` | "المساحة غير كافية" | Cancel export |
| Invalid path | `FileNotFoundError` | "المسار غير موجود" | Re-show folder dialog |
| PDF generation fail | `Exception` in PDF | "فشل إنشاء PDF للفاتورة {number}" | Skip & continue, report at end |
| Encoding error | `UnicodeError` | Fallback to ASCII | Auto-handle |

### Error Handling Code Pattern

```python
def safe_export(self, invoices, path):
    """Export with comprehensive error handling"""
    errors = []
    success_count = 0
    
    for invoice in invoices:
        try:
            self._export_single(invoice, path)
            success_count += 1
        except PermissionError:
            errors.append(f"Permission denied: {invoice['invoice_number']}")
        except Exception as e:
            errors.append(f"Error in {invoice['invoice_number']}: {str(e)}")
    
    return success_count, errors
```

---

## 📊 CSV Export Specification

### File Format
- **Encoding**: UTF-8 with BOM (`\ufeff`) for Excel Arabic support
- **Delimiter**: Comma (`,`)
- **Quote Character**: Double quote (`"`)
- **Line Ending**: Windows (`\r\n`)

### Column Structure

| # | Column Name (EN) | Column Name (AR) | Data Type | Example |
|---|------------------|------------------|-----------|---------|
| 1 | Invoice No | رقم الفاتورة | String | 2024100127 |
| 2 | Date | التاريخ | Date | 2025-03-06 |
| 3 | Time | الوقت | Time | 05:37:56 |
| 4 | Customer | العميل | String | فهد عبد المطيري |
| 5 | Customer Tax No | الرقم الضريبي | String | 0544054759 |
| 6 | Payment Type | نوع الدفع | String | نقدا |
| 7 | Subtotal | المجموع | Decimal | 6087.00 |
| 8 | Discount | الخصم | Decimal | 0.00 |
| 9 | Taxable Amount | الخاضع للضريبة | Decimal | 6087.00 |
| 10 | Tax Amount | الضريبة | Decimal | 913.05 |
| 11 | Net Total | الصافي | Decimal | 7000.05 |
| 12 | Status | الحالة | String | نشطة |

### Sample Output
```csv
رقم الفاتورة,التاريخ,الوقت,العميل,الرقم الضريبي,نوع الدفع,المجموع,الخصم,الخاضع للضريبة,الضريبة,الصافي,الحالة
2024100127,2025-03-06,05:37:56,فهد عبد المطيري,0544054759,نقدا,6087.00,0.00,6087.00,913.05,7000.05,نشطة
2024100126,2025-03-05,10:15:30,أحمد محمد,,نقدا,3043.48,0.00,3043.48,456.52,3500.00,نشطة
```

---

## 📄 PDF Export Specification

### File Naming Convention
```
Invoice_{invoice_number}.pdf

Examples:
- Invoice_2024100127.pdf
- Invoice_2024100126.pdf
```

### Batch Processing Strategy

```
For 100 invoices on low-spec hardware:

1. Process sequentially (not parallel) to limit memory
2. Generate one PDF at a time
3. Write to disk immediately (don't hold in memory)
4. Update progress after each file
5. Small delay between files (10ms) to keep UI responsive

Estimated time: ~2 seconds per invoice = 200 seconds for 100 invoices
```

---

## 🖥️ UI Components

### 1. Enhanced History Screen

```
┌──────────────────────────────────────────────────────────────────┐
│  سجل الفواتير - Invoice History                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🔍 بحث: [___________]  من: [📅_____] إلى: [📅_____] [بحث]      │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ☐ │ # │ رقم الفاتورة │ التاريخ    │ العميل      │ الإجمالي │  │
│  ├────────────────────────────────────────────────────────────┤  │
│  │ ☑ │ 1 │ 2024100127   │ 2025-03-06 │ فهد المطيري │ 7,000.05 │  │
│  │ ☑ │ 2 │ 2024100126   │ 2025-03-05 │ أحمد محمد   │ 3,500.00 │  │
│  │ ☐ │ 3 │ 2024100125   │ 2025-03-04 │ سعد العتيبي │12,650.00 │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ☑ تحديد الكل (2 محدد)                                           │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ 📊 تصدير CSV │  │ 📄 تصدير PDF │  │ 👁️ عرض      │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 2. Progress Dialog

```
┌─────────────────────────────────────────┐
│  جاري التصدير...                        │
├─────────────────────────────────────────┤
│                                         │
│  ████████████░░░░░░░░  60%              │
│                                         │
│  تصدير الفاتورة 6 من 10                 │
│  Invoice_2024100127.pdf ✓               │
│                                         │
│           ┌──────────┐                  │
│           │  إلغاء   │                  │
│           └──────────┘                  │
└─────────────────────────────────────────┘
```

### 3. Completion Dialog

```
┌─────────────────────────────────────────┐
│  ✓ اكتمل التصدير                        │
├─────────────────────────────────────────┤
│                                         │
│  تم تصدير 10 فواتير بنجاح               │
│                                         │
│  المجلد: C:\Users\...\Invoices          │
│                                         │
│  ┌──────────────┐  ┌──────────────┐     │
│  │ فتح المجلد   │  │    إغلاق    │     │
│  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────┘
```

---

## 📁 File Structure (New Files)

```
InvoiceApp/
├── app/
│   └── exporter.py          # NEW: Export logic (CSV + PDF)
│
└── ui/
    ├── invoice_history.py   # MODIFIED: Add checkboxes & export buttons
    └── export_dialog.py     # NEW: Progress dialog
```

---

## 🔧 Implementation Steps

### Step 1: Create Export Module (`app/exporter.py`)
- CSV export function
- PDF batch export function
- Progress callback support

### Step 2: Create Progress Dialog (`ui/export_dialog.py`)
- Progress bar
- Status text
- Cancel button
- Threading support

### Step 3: Modify History Screen (`ui/invoice_history.py`)
- Add checkbox column to Treeview
- Add "Select All" checkbox
- Add export buttons
- Connect to export functions

### Step 4: Testing
- Test with 1, 10, 100 invoices
- Test cancel mid-export
- Test permission errors
- Test Arabic characters in CSV

---

## ⏱️ Performance Estimates

| Operation | 10 Invoices | 100 Invoices | 1000 Invoices |
|-----------|-------------|--------------|---------------|
| CSV Export | < 1 sec | < 2 sec | < 5 sec |
| PDF Export | ~20 sec | ~200 sec | ~30 min |
| Memory Usage | < 50 MB | < 100 MB | < 150 MB |

---

## ✅ Acceptance Criteria

- [x] User can select multiple invoices with checkboxes
- [x] "Select All" checkbox works correctly
- [x] CSV export creates single file with all selected invoices
- [x] CSV opens correctly in Excel with Arabic text
- [x] PDF export creates individual files per invoice
- [x] PDF files follow original invoice layout
- [x] Progress dialog shows during export
- [x] User can cancel export mid-process
- [x] Error messages are user-friendly (Arabic)
- [x] Export works offline
- [x] UI doesn't freeze during export
- [x] "Open Folder" button works after export

---

## 🎉 Implementation Status: COMPLETED

**Implemented files:**
- `app/exporter.py` - InvoiceExporter class with CSV/PDF export logic
- `ui/export_dialog.py` - ExportProgressDialog with threaded export
- `ui/invoice_history.py` - Enhanced with checkboxes and export button

*Plan created: January 28, 2026*
*Implementation completed: January 28, 2026*
