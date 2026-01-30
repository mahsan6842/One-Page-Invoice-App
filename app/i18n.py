"""
Simple i18n utilities for the InvoiceApp (Arabic/English).

- No external dependencies
- Stable translation keys (avoid hardcoding UI strings everywhere)
"""

from __future__ import annotations

from typing import Dict, List, Callable

LANG_AR = "ar"
LANG_EN = "en"

# Canonical unit keys (storage-neutral); Arabic: حبة, متر, كيلو, قطعة, علبة
UNIT_KEYS = ['piece', 'meter', 'kg', 'unit', 'box']
UNIT_DISPLAY: Dict[str, Dict[str, str]] = {
    'piece': {LANG_AR: 'حبة', LANG_EN: 'Piece'},
    'meter': {LANG_AR: 'متر', LANG_EN: 'Meter'},
    'kg': {LANG_AR: 'كيلو', LANG_EN: 'Kg'},
    'unit': {LANG_AR: 'قطعة', LANG_EN: 'Unit'},
    'box': {LANG_AR: 'علبة', LANG_EN: 'Box'},
}
# Reverse: display value -> canonical key
_AR_TO_KEY = {v[LANG_AR]: k for k, v in UNIT_DISPLAY.items()}
_EN_TO_KEY = {v[LANG_EN]: k for k, v in UNIT_DISPLAY.items()}

_current_lang = LANG_AR
_language_change_callbacks: List[Callable[[str], None]] = []


def set_current_lang(lang: str) -> None:
    global _current_lang
    _current_lang = (lang or LANG_AR).lower()
    for callback in _language_change_callbacks:
        try:
            callback(_current_lang)
        except Exception:
            pass


def get_current_lang() -> str:
    return _current_lang or LANG_AR


def subscribe_language_change(callback: Callable[[str], None]) -> None:
    """Register a callback to be invoked when language changes."""
    if callback not in _language_change_callbacks:
        _language_change_callbacks.append(callback)


def unsubscribe_language_change(callback: Callable[[str], None]) -> None:
    """Remove a language change callback."""
    if callback in _language_change_callbacks:
        _language_change_callbacks.remove(callback)


def is_rtl(lang: str) -> bool:
    return (lang or LANG_AR).lower().startswith("ar")


def pack_side(lang: str) -> str:
    """Return pack side for main content: 'right' for RTL, 'left' for LTR."""
    return 'right' if is_rtl(lang) else 'left'


def pack_side_opposite(lang: str) -> str:
    """Return pack side for scrollbar/auxiliary: 'left' for RTL, 'right' for LTR."""
    return 'left' if is_rtl(lang) else 'right'


def anchor_for(lang: str) -> str:
    """Return text anchor: 'e' (east) for RTL, 'w' (west) for LTR."""
    return 'e' if is_rtl(lang) else 'w'


def grid_column_label(lang: str) -> int:
    """Grid column for labels: 1 in RTL, 0 in LTR."""
    return 1 if is_rtl(lang) else 0


def grid_column_value(lang: str) -> int:
    """Grid column for values: 0 in RTL, 1 in LTR."""
    return 0 if is_rtl(lang) else 1


def sticky_for(lang: str) -> str:
    """Grid sticky for label/value alignment: 'e' in RTL, 'w' in LTR."""
    return 'e' if is_rtl(lang) else 'w'


def justify_for(lang: str) -> str:
    """Entry justify: 'right' in RTL, 'left' in LTR."""
    return 'right' if is_rtl(lang) else 'left'


def tree_anchor_for(lang: str) -> str:
    """Treeview column anchor: 'e' in RTL, 'w' in LTR."""
    return 'e' if is_rtl(lang) else 'w'


def pack_anchor_for(lang: str) -> str:
    """Pack anchor for frames: 'e' in RTL, 'w' in LTR."""
    return 'e' if is_rtl(lang) else 'w'


# Stable keys -> language -> translation
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # App / common
    "app.title": {LANG_AR: "نظام الفواتير - Invoice System", LANG_EN: "Invoice System"},
    "common.ready": {LANG_AR: "جاهز", LANG_EN: "Ready"},
    "common.success": {LANG_AR: "نجاح", LANG_EN: "Success"},
    "common.error": {LANG_AR: "خطأ", LANG_EN: "Error"},
    "common.confirm": {LANG_AR: "تأكيد", LANG_EN: "Confirm"},
    "common.close": {LANG_AR: "✖️ إغلاق", LANG_EN: "✖️ Close"},
    "common.search": {LANG_AR: "بحث", LANG_EN: "Search"},
    "common.from": {LANG_AR: "من:", LANG_EN: "From:"},
    "common.to": {LANG_AR: "إلى:", LANG_EN: "To:"},

    # Menus
    "menu.file": {LANG_AR: "ملف", LANG_EN: "File"},
    "menu.view": {LANG_AR: "عرض", LANG_EN: "View"},
    "menu.help": {LANG_AR: "مساعدة", LANG_EN: "Help"},
    "menu.language": {LANG_AR: "اللغة", LANG_EN: "Language"},
    "menu.language.ar": {LANG_AR: "العربية", LANG_EN: "Arabic"},
    "menu.language.en": {LANG_AR: "English", LANG_EN: "English"},
    "menu.newInvoice": {LANG_AR: "فاتورة جديدة", LANG_EN: "New Invoice"},
    "menu.backup": {LANG_AR: "نسخ احتياطي", LANG_EN: "Backup"},
    "menu.exit": {LANG_AR: "خروج", LANG_EN: "Exit"},
    "menu.home": {LANG_AR: "الرئيسية", LANG_EN: "Home"},
    "menu.history": {LANG_AR: "سجل الفواتير", LANG_EN: "Invoice History"},
    "menu.settings": {LANG_AR: "الإعدادات", LANG_EN: "Settings"},
    "menu.about": {LANG_AR: "حول البرنامج", LANG_EN: "About"},

    # Tabs / toolbar
    "tab.home": {LANG_AR: "   🏠 الرئيسية   ", LANG_EN: "   🏠 Home   "},
    "tab.history": {LANG_AR: "   📋 سجل الفواتير   ", LANG_EN: "   📋 History   "},
    "tab.settings": {LANG_AR: "   ⚙️ الإعدادات   ", LANG_EN: "   ⚙️ Settings   "},
    "toolbar.home": {LANG_AR: "🏠 الرئيسية", LANG_EN: "🏠 Home"},
    "toolbar.history": {LANG_AR: "📋 السجل", LANG_EN: "📋 History"},
    "toolbar.settings": {LANG_AR: "⚙️ الإعدادات", LANG_EN: "⚙️ Settings"},
    "toolbar.newInvoice": {LANG_AR: "➕ فاتورة جديدة", LANG_EN: "➕ New Invoice"},

    # About / exit
    "about.title": {LANG_AR: "حول البرنامج", LANG_EN: "About"},
    "about.body": {
        LANG_AR: "نظام الفواتير\nInvoice System\n\nإصدار 1.0.0\nVersion 1.0.0\n\nنظام لإدارة وطباعة الفواتير\nمع دعم ضريبة القيمة المضافة",
        LANG_EN: "Invoice System\n\nVersion 1.0.0\n\nOffline invoice management with VAT support and ZATCA QR.",
    },
    "exit.title": {LANG_AR: "تأكيد الخروج", LANG_EN: "Exit"},
    "exit.body": {LANG_AR: "هل أنت متأكد من الخروج؟", LANG_EN: "Are you sure you want to exit?"},

    # Invoice history
    "history.searchLabel": {LANG_AR: "🔍 بحث:", LANG_EN: "🔍 Search:"},
    "history.selectAll": {LANG_AR: "تحديد الكل", LANG_EN: "Select all"},
    "history.clearSelection": {LANG_AR: "إلغاء التحديد", LANG_EN: "Clear selection"},
    "history.selectedCount": {LANG_AR: "({count} محدد)", LANG_EN: "({count} selected)"},
    "history.exportGroup": {LANG_AR: "تصدير", LANG_EN: "Export"},
    "history.exportCsv": {LANG_AR: "📊 تصدير CSV / Excel", LANG_EN: "📊 Export CSV / Excel"},
    "history.exportPdf": {LANG_AR: "📄 تصدير PDF", LANG_EN: "📄 Export PDF"},
    "history.exportHint": {LANG_AR: "حدد الفواتير للتصدير", LANG_EN: "Select invoices to export"},
    "history.action.view": {LANG_AR: "👁️ عرض", LANG_EN: "👁️ View"},
    "history.action.print": {LANG_AR: "🖨️ طباعة", LANG_EN: "🖨️ Print"},
    "history.action.cancel": {LANG_AR: "❌ إلغاء", LANG_EN: "❌ Cancel"},
    "history.action.refresh": {LANG_AR: "🔄 تحديث", LANG_EN: "🔄 Refresh"},
    "history.summary.count": {LANG_AR: "إجمالي الفواتير: {count}", LANG_EN: "Total invoices: {count}"},
    "history.summary.total": {LANG_AR: "إجمالي المبيعات: {total} ريال", LANG_EN: "Total sales: {total} SAR"},
    "history.page": {LANG_AR: "صفحة {page}", LANG_EN: "Page {page}"},
    "history.col.select": {LANG_AR: "☐", LANG_EN: "☐"},
    "history.col.row": {LANG_AR: "#", LANG_EN: "#"},
    "history.col.number": {LANG_AR: "رقم الفاتورة", LANG_EN: "Invoice No"},
    "history.col.date": {LANG_AR: "التاريخ", LANG_EN: "Date"},
    "history.col.customer": {LANG_AR: "العميل", LANG_EN: "Customer"},
    "history.col.total": {LANG_AR: "الإجمالي", LANG_EN: "Total"},
    "history.col.status": {LANG_AR: "الحالة", LANG_EN: "Status"},
    "status.active": {LANG_AR: "نشطة", LANG_EN: "Active"},
    "status.cancelled": {LANG_AR: "ملغاة", LANG_EN: "Cancelled"},

    # Invoice view
    "view.invoiceTitle": {LANG_AR: "فاتورة رقم {number}", LANG_EN: "Invoice #{number}"},
    "view.header": {LANG_AR: "فاتورة رقم: {number}", LANG_EN: "Invoice #: {number}"},
    "view.detailsGroup": {LANG_AR: "تفاصيل الفاتورة", LANG_EN: "Invoice details"},
    "view.itemsGroup": {LANG_AR: "الأصناف", LANG_EN: "Items"},
    "view.totalsGroup": {LANG_AR: "الإجماليات", LANG_EN: "Totals"},
    "view.label.date": {LANG_AR: "التاريخ:", LANG_EN: "Date:"},
    "view.label.time": {LANG_AR: "الوقت:", LANG_EN: "Time:"},
    "view.label.customer": {LANG_AR: "العميل:", LANG_EN: "Customer:"},
    "view.label.payment": {LANG_AR: "نوع الدفع:", LANG_EN: "Payment:"},
    "view.col.item": {LANG_AR: "الصنف", LANG_EN: "Item"},
    "view.col.qty": {LANG_AR: "الكمية", LANG_EN: "Qty"},
    "view.col.price": {LANG_AR: "السعر", LANG_EN: "Price"},
    "view.col.total": {LANG_AR: "الإجمالي", LANG_EN: "Total"},
    "view.col.tax": {LANG_AR: "الضريبة", LANG_EN: "Tax"},
    "view.col.net": {LANG_AR: "الصافي", LANG_EN: "Net"},
    "view.total.subtotal": {LANG_AR: "المجموع:", LANG_EN: "Subtotal:"},
    "view.total.discount": {LANG_AR: "الخصم:", LANG_EN: "Discount:"},
    "view.total.taxable": {LANG_AR: "الخاضع للضريبة:", LANG_EN: "Taxable:"},
    "view.total.vat": {LANG_AR: "ضريبة 15%:", LANG_EN: "VAT (15%):"},
    "view.total.net": {LANG_AR: "الصافي شامل الضريبة:", LANG_EN: "Total (incl. VAT):"},
    "view.btn.print": {LANG_AR: "🖨️ طباعة", LANG_EN: "🖨️ Print"},
    "view.btn.savePdf": {LANG_AR: "💾 حفظ PDF", LANG_EN: "💾 Save PDF"},
    "view.pdf.missing": {LANG_AR: "⚠️ مكتبة PDF غير مثبتة", LANG_EN: "⚠️ PDF library not installed"},
    "view.pdf.generated": {LANG_AR: "✓ تم إنشاء PDF", LANG_EN: "✓ PDF generated"},
    "view.print.sent": {LANG_AR: "✓ تم إرسال للطباعة", LANG_EN: "✓ Sent to printer"},
    "view.save.done": {LANG_AR: "✓ تم الحفظ", LANG_EN: "✓ Saved"},
    "view.save.success": {LANG_AR: "تم حفظ الفاتورة في:\n{path}", LANG_EN: "Invoice saved to:\n{path}"},
    "view.err.pdfCreate": {LANG_AR: "فشل إنشاء ملف PDF", LANG_EN: "Failed to generate PDF"},
    "view.err.print": {LANG_AR: "فشلت الطباعة: {error}", LANG_EN: "Printing failed: {error}"},
    "view.err.save": {LANG_AR: "فشل الحفظ: {error}", LANG_EN: "Save failed: {error}"},
    "view.err.generic": {LANG_AR: "خطأ: {error}", LANG_EN: "Error: {error}"},

    # Form labels and messages
    "form.customerInfo": {LANG_AR: "معلومات العميل", LANG_EN: "Customer info"},
    "form.items": {LANG_AR: "الأصناف", LANG_EN: "Items"},
    "form.totals": {LANG_AR: "الإجماليات", LANG_EN: "Totals"},
    "form.taxNumber": {LANG_AR: "الرقم الضريبي:", LANG_EN: "Tax number:"},
    "form.customerName": {LANG_AR: "اسم العميل:", LANG_EN: "Customer name:"},
    "form.address": {LANG_AR: "العنوان:", LANG_EN: "Address:"},
    "form.phone": {LANG_AR: "الهاتف:", LANG_EN: "Phone:"},
    "form.payment": {LANG_AR: "نوع الدفع:", LANG_EN: "Payment:"},
    "form.addItem": {LANG_AR: "+ إضافة صنف", LANG_EN: "+ Add item"},
    "form.subtotal": {LANG_AR: "المجموع:", LANG_EN: "Subtotal:"},
    "form.discountPct": {LANG_AR: "الخصم (%):", LANG_EN: "Discount (%):"},
    "form.taxable": {LANG_AR: "الخاضع للضريبة:", LANG_EN: "Taxable:"},
    "form.vat15": {LANG_AR: "ضريبة 15%:", LANG_EN: "VAT (15%):"},
    "form.netTotal": {LANG_AR: "الصافي شامل الضريبة:", LANG_EN: "Total (incl. VAT):"},
    "form.btnClear": {LANG_AR: "❌ إلغاء", LANG_EN: "❌ Clear"},
    "form.btnSavePrint": {LANG_AR: "🖨️ حفظ وطباعة", LANG_EN: "🖨️ Save & Print"},
    "form.btnSave": {LANG_AR: "💾 حفظ", LANG_EN: "💾 Save"},
    "form.discountArrow": {LANG_AR: " ← ", LANG_EN: " → "},
    "form.colItem": {LANG_AR: "الصنف", LANG_EN: "Item"},
    "form.colUnit": {LANG_AR: "الوحدة", LANG_EN: "Unit"},
    "form.colQty": {LANG_AR: "الكمية", LANG_EN: "Qty"},
    "form.colPrice": {LANG_AR: "السعر", LANG_EN: "Price"},
    "form.colTotal": {LANG_AR: "الإجمالي", LANG_EN: "Total"},
    "form.colDiscPct": {LANG_AR: "خصم%", LANG_EN: "Disc%"},
    "form.colTax": {LANG_AR: "الضريبة", LANG_EN: "Tax"},
    "form.colNet": {LANG_AR: "الصافي", LANG_EN: "Net"},

    # Warnings and messages
    "msg.warning": {LANG_AR: "تنبيه", LANG_EN: "Warning"},
    "msg.invoiceSaved": {LANG_AR: "تم حفظ الفاتورة رقم {number}", LANG_EN: "Invoice {number} saved"},
    "msg.invoiceSavedShort": {LANG_AR: "تم حفظ الفاتورة رقم {number}", LANG_EN: "Invoice {number} saved"},
    "msg.selectOneExport": {LANG_AR: "يرجى تحديد فاتورة واحدة على الأقل للتصدير", LANG_EN: "Please select at least one invoice to export."},
    "msg.selectInvoiceView": {LANG_AR: "يرجى اختيار فاتورة للعرض", LANG_EN: "Please select an invoice to view."},
    "msg.selectInvoicePrint": {LANG_AR: "يرجى اختيار فاتورة للطباعة", LANG_EN: "Please select an invoice to print."},
    "msg.selectInvoice": {LANG_AR: "يرجى اختيار فاتورة", LANG_EN: "Please select an invoice."},
    "msg.confirmCancelInvoice": {LANG_AR: "هل أنت متأكد من إلغاء هذه الفاتورة؟", LANG_EN: "Are you sure you want to cancel this invoice?"},
    "msg.invoiceCancelled": {LANG_AR: "تم إلغاء الفاتورة", LANG_EN: "Invoice cancelled."},
    "msg.minOneItem": {LANG_AR: "يجب أن تحتوي الفاتورة على صنف واحد على الأقل", LANG_EN: "An invoice must contain at least one item."},
    "msg.addOneItem": {LANG_AR: "يرجى إضافة صنف واحد على الأقل", LANG_EN: "Please add at least one item."},
    "msg.itemQtyPositive": {LANG_AR: "الصنف {i}: الكمية يجب أن تكون أكبر من صفر", LANG_EN: "Item {i}: quantity must be greater than 0."},
    "msg.itemPriceNegative": {LANG_AR: "الصنف {i}: السعر لا يمكن أن يكون سالباً", LANG_EN: "Item {i}: price cannot be negative."},
    "msg.saveFailed": {LANG_AR: "حدث خطأ أثناء الحفظ: {error}", LANG_EN: "Save failed: {error}"},
    "msg.errorOccurred": {LANG_AR: "حدث خطأ: {error}", LANG_EN: "Error: {error}"},
    "msg.settingsSaved": {LANG_AR: "تم حفظ الإعدادات بنجاح", LANG_EN: "Settings saved successfully."},
    "msg.settingsSaveFailed": {LANG_AR: "فشل حفظ الإعدادات: {error}", LANG_EN: "Failed to save settings: {error}"},
    "msg.backupCreated": {LANG_AR: "تم إنشاء النسخة الاحتياطية:\n{path}", LANG_EN: "Backup created:\n{path}"},
    "msg.backupFailed": {LANG_AR: "فشل إنشاء النسخة الاحتياطية", LANG_EN: "Backup failed."},
    "msg.confirmRestore": {LANG_AR: "سيتم استبدال قاعدة البيانات الحالية.\nهل أنت متأكد من المتابعة؟", LANG_EN: "This will replace the current database.\nDo you want to continue?"},
    "msg.restoreSuccess": {LANG_AR: "تم استعادة النسخة الاحتياطية بنجاح", LANG_EN: "Backup restored successfully."},
    "msg.restoreFailed": {LANG_AR: "فشلت الاستعادة: {error}", LANG_EN: "Restore failed: {error}"},
    "msg.readyExport": {LANG_AR: "جاهز لتصدير {count} فاتورة", LANG_EN: "Ready to export {count} invoice(s)"},

    # Settings
    "settings.companyInfo": {LANG_AR: "بيانات المؤسسة", LANG_EN: "Company info"},
    "settings.companyName": {LANG_AR: "اسم المؤسسة:", LANG_EN: "Company name:"},
    "settings.address": {LANG_AR: "العنوان:", LANG_EN: "Address:"},
    "settings.taxNumber": {LANG_AR: "الرقم الضريبي:", LANG_EN: "VAT / Tax number:"},
    "settings.phone1": {LANG_AR: "الهاتف 1:", LANG_EN: "Phone 1:"},
    "settings.phone2": {LANG_AR: "الهاتف 2:", LANG_EN: "Phone 2:"},
    "settings.logo": {LANG_AR: "الشعار:", LANG_EN: "Logo:"},
    "settings.browse": {LANG_AR: "اختيار...", LANG_EN: "Browse..."},
    "settings.invoiceSettings": {LANG_AR: "إعدادات الفاتورة", LANG_EN: "Invoice settings"},
    "settings.vatRate": {LANG_AR: "نسبة الضريبة (%):", LANG_EN: "VAT rate (%):"},
    "settings.invoicePrefix": {LANG_AR: "بادئة رقم الفاتورة:", LANG_EN: "Invoice prefix:"},
    "settings.nextNumber": {LANG_AR: "الرقم التالي:", LANG_EN: "Next number:"},
    "settings.termsConditions": {LANG_AR: "الشروط والأحكام", LANG_EN: "Terms & Conditions"},
    "settings.termsHint": {LANG_AR: "(أدخل كل شرط في سطر منفصل)", LANG_EN: "(Enter one term per line)"},
    "settings.backup": {LANG_AR: "النسخ الاحتياطي", LANG_EN: "Backup"},
    "settings.createBackup": {LANG_AR: "💾 إنشاء نسخة احتياطية", LANG_EN: "💾 Create backup"},
    "settings.restoreBackup": {LANG_AR: "📂 استعادة من نسخة", LANG_EN: "📂 Restore backup"},
    "settings.saveSettings": {LANG_AR: "💾 حفظ الإعدادات", LANG_EN: "💾 Save settings"},
    "settings.reload": {LANG_AR: "🔄 إعادة تحميل", LANG_EN: "🔄 Reload"},

    # Export dialog
    "export.titleCsv": {LANG_AR: "تصدير CSV", LANG_EN: "Export CSV"},
    "export.titlePdf": {LANG_AR: "تصدير PDF", LANG_EN: "Export PDF"},
    "export.exporting": {LANG_AR: "جاري التصدير...", LANG_EN: "Exporting..."},
    "export.preparing": {LANG_AR: "جاري التحضير...", LANG_EN: "Preparing..."},
    "export.cancel": {LANG_AR: "إلغاء", LANG_EN: "Cancel"},
    "export.done": {LANG_AR: "اكتمل!", LANG_EN: "Done!"},
    "export.error": {LANG_AR: "خطأ في التصدير", LANG_EN: "Export error"},
    "export.complete": {LANG_AR: "اكتمل التصدير", LANG_EN: "Export complete"},
    "export.successCount": {LANG_AR: "تم تصدير {count} فاتورة بنجاح", LANG_EN: "Exported {count} invoice(s) successfully."},
    "export.partialCount": {LANG_AR: "تم تصدير {success} من {total} فاتورة", LANG_EN: "Exported {success} of {total} invoice(s)."},
    "export.failed": {LANG_AR: "فشل التصدير", LANG_EN: "Export failed."},
    "export.errorDetail": {LANG_AR: "حدث خطأ: {error}", LANG_EN: "Error: {error}"},
    "export.errorsCount": {LANG_AR: "({count} أخطاء)", LANG_EN: "({count} errors)"},
    "export.openFolder": {LANG_AR: "فتح المجلد", LANG_EN: "Open folder"},
    "export.close": {LANG_AR: "إغلاق", LANG_EN: "Close"},
    "export.cancelling": {LANG_AR: "جاري الإلغاء...", LANG_EN: "Cancelling..."},
    "export.options": {LANG_AR: "خيارات التصدير", LANG_EN: "Export options"},
    "export.headerCount": {LANG_AR: "تصدير {count} فاتورة", LANG_EN: "Export {count} invoice(s)"},
    "export.type": {LANG_AR: "نوع التصدير", LANG_EN: "Export type"},
    "export.csvHint": {LANG_AR: "(ملف واحد - {time})", LANG_EN: "(single file - {time})"},
    "export.pdfHint": {LANG_AR: "(ملفات منفصلة - {time})", LANG_EN: "(separate files - {time})"},
    "export.export": {LANG_AR: "تصدير", LANG_EN: "Export"},
    "export.csvDesc": {LANG_AR: "سيتم تصدير جميع الفواتير المحددة في ملف CSV واحد يمكن فتحه في Excel.", LANG_EN: "All selected invoices will be exported to a single CSV file (Excel-friendly)."},
    "export.pdfDesc": {LANG_AR: "سيتم إنشاء ملف PDF منفصل لكل فاتورة في المجلد المحدد.", LANG_EN: "A separate PDF will be generated for each invoice in the selected folder."},
    "export.saveCsv": {LANG_AR: "حفظ ملف CSV", LANG_EN: "Save CSV"},
    "export.choosePdfFolder": {LANG_AR: "اختر مجلد حفظ ملفات PDF", LANG_EN: "Choose PDF output folder"},

    # Currency
    "currency.sar": {LANG_AR: "ريال", LANG_EN: "SAR"},
}


def t(key: str, lang: str = None, **kwargs) -> str:
    """
    Translate key for given language. Falls back to English then key itself.
    Supports .format(**kwargs).
    If lang is None, uses get_current_lang().
    """
    lang = (lang or get_current_lang() or LANG_AR).lower()
    entry = TRANSLATIONS.get(key)
    if not entry:
        text = key
    else:
        text = entry.get(lang) or entry.get(LANG_EN) or entry.get(LANG_AR) or key
    try:
        return text.format(**kwargs)
    except Exception:
        return text


def t_current(key: str, **kwargs) -> str:
    """Shorthand for t(key, get_current_lang(), **kwargs)."""
    return t(key, get_current_lang(), **kwargs)


def translate_payment_type(value: str, lang: str) -> str:
    """Translate stored payment type values for display."""
    v = (value or "").strip()
    if not v:
        return ""
    mapping = {
        "نقدا": {LANG_AR: "نقدا", LANG_EN: "Cash"},
        "آجل": {LANG_AR: "آجل", LANG_EN: "Credit"},
        "تحويل بنكي": {LANG_AR: "تحويل بنكي", LANG_EN: "Bank transfer"},
        "cash": {LANG_AR: "نقدا", LANG_EN: "Cash"},
        "credit": {LANG_AR: "آجل", LANG_EN: "Credit"},
        "bank_transfer": {LANG_AR: "تحويل بنكي", LANG_EN: "Bank transfer"},
    }
    if v in mapping:
        return mapping[v].get(lang, mapping[v].get(LANG_EN, v))
    return v


def payment_type_to_storage(value: str) -> str:
    """Convert payment display value to storage (Arabic)."""
    v = (value or "").strip().lower()
    if not v:
        return "نقدا"
    mapping = {"cash": "نقدا", "credit": "آجل", "bank transfer": "تحويل بنكي",
               "نقدا": "نقدا", "آجل": "آجل", "تحويل بنكي": "تحويل بنكي"}
    return mapping.get(v, value)


def translate_unit(value: str, lang: str) -> str:
    """Translate unit value for display. Accepts Arabic, English, or canonical key."""
    v = (value or "").strip()
    if not v:
        return ""
    lang = (lang or LANG_AR).lower()
    key = _AR_TO_KEY.get(v) or _EN_TO_KEY.get(v) or (v if v in UNIT_DISPLAY else None)
    if key and key in UNIT_DISPLAY:
        return UNIT_DISPLAY[key].get(lang, UNIT_DISPLAY[key].get(LANG_EN, v))
    return v


def get_unit_display_values(lang: str) -> List[str]:
    """Return unit options for combobox in the given language."""
    lang = (lang or LANG_AR).lower()
    return [UNIT_DISPLAY[k].get(lang, UNIT_DISPLAY[k].get(LANG_EN, k)) for k in UNIT_KEYS]


def unit_to_canonical(value: str) -> str:
    """Convert display value (AR or EN) to canonical key for storage. Returns value as-is if unknown."""
    v = (value or "").strip()
    if not v:
        return "piece"
    return _AR_TO_KEY.get(v) or _EN_TO_KEY.get(v) or v

