"""
Simple i18n utilities for the InvoiceApp (Arabic/English).

- No external dependencies
- Stable translation keys (avoid hardcoding UI strings everywhere)
"""

from __future__ import annotations

from typing import Dict

LANG_AR = "ar"
LANG_EN = "en"

_current_lang = LANG_AR


def set_current_lang(lang: str) -> None:
    global _current_lang
    _current_lang = (lang or LANG_AR).lower()


def get_current_lang() -> str:
    return _current_lang or LANG_AR


def is_rtl(lang: str) -> bool:
    return (lang or LANG_AR).lower().startswith("ar")


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
}


def t(key: str, lang: str, **kwargs) -> str:
    """
    Translate key for given language. Falls back to English then key itself.
    Supports .format(**kwargs).
    """
    lang = (lang or LANG_AR).lower()
    entry = TRANSLATIONS.get(key)
    if not entry:
        text = key
    else:
        text = entry.get(lang) or entry.get(LANG_EN) or entry.get(LANG_AR) or key
    try:
        return text.format(**kwargs)
    except Exception:
        return text


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

