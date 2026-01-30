"""
Invoice Application - PDF Generator
Generates PDF invoices matching the Saudi invoice layout with Arabic support
"""

from __future__ import annotations

import os
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    A4 = (595.27, 841.89)  # Default A4 dimensions in points
    canvas = None  # type: ignore
    colors = None  # type: ignore
    print("Warning: reportlab not installed. PDF generation will not work.")

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_AVAILABLE = True
except ImportError:
    ARABIC_AVAILABLE = False
    print("Warning: arabic-reshaper or python-bidi not installed. Arabic text may not display correctly.")

from app.qr_generator import generate_invoice_qr, QR_AVAILABLE
from app.i18n import translate_unit, LANG_AR, get_current_lang


class ArabicPDFGenerator:
    """
    PDF Generator for Arabic invoices
    Handles RTL text, custom fonts, and ZATCA-compliant QR codes
    """
    
    # Page dimensions (A4)
    PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27, 841.89 points
    MARGIN = 40
    
    def __init__(self, font_path: str = None):
        """
        Initialize PDF generator with Arabic font
        
        Args:
            font_path: Path to Arabic TTF font (optional)
        """
        self.font_path = font_path
        self.font_registered = False
        self._register_font()
    
    def _register_font(self):
        """Register Arabic font with ReportLab"""
        if not PDF_AVAILABLE:
            return
        
        # Try to find font in common locations
        font_paths = [
            self.font_path,
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'Amiri-Regular.ttf'),
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'Cairo-Regular.ttf'),
            'C:/Windows/Fonts/arial.ttf',  # Fallback
        ]
        
        for path in font_paths:
            if path and os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont('Arabic', path))
                    self.font_registered = True
                    print(f"Registered font: {path}")
                    return
                except Exception as e:
                    print(f"Failed to register font {path}: {e}")
        
        print("Warning: No Arabic font found. Using default font.")
    
    def arabic_text(self, text: str) -> str:
        """
        Reshape and reorder Arabic text for proper display
        
        Args:
            text: Arabic text string
            
        Returns:
            Properly shaped and ordered text for PDF
        """
        if not text:
            return ''
        
        if ARABIC_AVAILABLE:
            try:
                reshaped = arabic_reshaper.reshape(text)
                return get_display(reshaped)
            except Exception:
                pass
        
        return text
    
    def format_number(self, number: float, decimals: int = 2) -> str:
        """Format number with commas and decimal places"""
        return f"{number:,.{decimals}f}"
    
    def generate_invoice_pdf(
        self,
        invoice_data: Dict[str, Any],
        company_settings: Dict[str, Any],
        output_path: str = None
    ) -> Optional[bytes]:
        """
        Generate PDF invoice
        
        Args:
            invoice_data: Invoice data dictionary with items
            company_settings: Company settings dictionary
            output_path: Optional path to save PDF file
            
        Returns:
            PDF bytes if output_path is None, else saves to file and returns None
        """
        if not PDF_AVAILABLE:
            print("ReportLab not installed. Cannot generate PDF.")
            return None
        
        # Create buffer or file
        if output_path:
            buffer = output_path
        else:
            buffer = BytesIO()
        
        # Create canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Set default font
        font_name = 'Arabic' if self.font_registered else 'Helvetica'
        
        try:
            lang = company_settings.get('ui_language') or get_current_lang() or LANG_AR
            self._draw_header(c, company_settings, font_name)
            self._draw_invoice_info(c, invoice_data, font_name)
            self._draw_customer_info(c, invoice_data, font_name)
            self._draw_items_table(c, invoice_data, font_name, lang)
            self._draw_totals_and_qr(c, invoice_data, company_settings, font_name)
            self._draw_terms(c, company_settings, font_name)
            self._draw_signature(c, font_name)
            
            c.save()
            
            if output_path:
                return None
            else:
                return buffer.getvalue()
                
        except Exception as e:
            print(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _draw_header(self, c: canvas.Canvas, settings: dict, font_name: str):
        """Draw company header"""
        y = self.PAGE_HEIGHT - self.MARGIN
        
        # Company name (large, centered or right-aligned for Arabic)
        c.setFont(font_name, 18)
        company_name = self.arabic_text(settings.get('company_name_ar', ''))
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, company_name)
        
        y -= 20
        
        # Address
        c.setFont(font_name, 10)
        address = self.arabic_text(settings.get('address_ar', ''))
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, address)
        
        y -= 15
        
        # Tax number
        tax_label = self.arabic_text("الرقم الضريبي:")
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, 
                         f"{settings.get('tax_number', '')} :{tax_label}")
        
        y -= 15
        
        # Contact numbers
        phones = self.arabic_text("للتواصل:")
        phone_text = f"{settings.get('phone1', '')} - {settings.get('phone2', '')}"
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, f"{phone_text} {phones}")
        
        # Draw horizontal line
        y -= 10
        c.setStrokeColor(colors.grey)
        c.line(self.MARGIN, y, self.PAGE_WIDTH - self.MARGIN, y)
    
    def _draw_invoice_info(self, c: canvas.Canvas, invoice: dict, font_name: str):
        """Draw invoice information box"""
        y = self.PAGE_HEIGHT - 130
        
        # Invoice title box (left side)
        c.setFont(font_name, 14)
        title = self.arabic_text("فاتورة مبيعات")
        c.drawRightString(200, y, title)
        
        c.setFont(font_name, 10)
        subtitle = self.arabic_text("فاتورة ضريبية مبسطة")
        c.drawRightString(200, y - 18, subtitle)
        
        # Invoice details (right side)
        c.setFont(font_name, 10)
        
        # Invoice number
        inv_label = self.arabic_text("الفاتورة")
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, 
                         f"{invoice.get('invoice_number', '')} #{inv_label} #INVOICE")
        
        y -= 15
        
        # Date
        date_label = self.arabic_text("التاريخ")
        inv_date = invoice.get('invoice_date', '')
        inv_time = invoice.get('invoice_time', '')
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, 
                         f"{inv_time} {inv_date} :DATE {date_label}")
        
        y -= 15
        
        # Payment type
        payment_label = self.arabic_text("نوع الدفع")
        payment_value = self.arabic_text(invoice.get('payment_type', 'نقدا'))
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, 
                         f"{payment_value} :PAYMENT {payment_label}")
        
        y -= 15
        
        # Salesperson
        seller_label = self.arabic_text("البائع")
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, 
                         f"{invoice.get('salesperson', 'admin')} :SALER {seller_label}")
    
    def _draw_customer_info(self, c: canvas.Canvas, invoice: dict, font_name: str):
        """Draw customer information section"""
        y = self.PAGE_HEIGHT - 210
        
        c.setStrokeColor(colors.grey)
        c.line(self.MARGIN, y + 10, self.PAGE_WIDTH - self.MARGIN, y + 10)
        
        c.setFont(font_name, 10)
        
        # Customer name
        cust_label = self.arabic_text("العميل Customer:")
        cust_name = self.arabic_text(invoice.get('customer_name', ''))
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, f"{cust_name} {cust_label}")
        
        # Tax number (same line, left portion)
        tax_label = self.arabic_text("ر.الضريبي Tax Number:")
        c.drawRightString(300, y, f"{invoice.get('customer_tax_number', '')} {tax_label}")
        
        y -= 15
        
        # Phone
        phone_label = self.arabic_text("الهاتف Phone:")
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, 
                         f"{invoice.get('customer_phone', '')} {phone_label}")
        
        # Address
        addr_label = self.arabic_text("العنوان Address:")
        addr = self.arabic_text(invoice.get('customer_address', ''))
        c.drawRightString(300, y, f"{addr} {addr_label}")
        
        # Line after customer info
        y -= 10
        c.line(self.MARGIN, y, self.PAGE_WIDTH - self.MARGIN, y)
    
    def _draw_items_table(self, c: canvas.Canvas, invoice: dict, font_name: str, lang: str = None):
        """Draw items table"""
        lang = lang or LANG_AR
        y = self.PAGE_HEIGHT - 260
        
        items = invoice.get('items', [])
        
        # Table headers (RTL order)
        headers = [
            self.arabic_text('الصافي\nNET'),
            self.arabic_text('الضريبة\nTAX'),
            self.arabic_text('الخصم\nDiscount'),
            self.arabic_text('الاجمالي\nTotal'),
            self.arabic_text('السعر\nPrice'),
            self.arabic_text('الكمية\nQTY'),
            self.arabic_text('الوحدة\nUnit'),
            self.arabic_text('الصنف\nItems'),
            self.arabic_text('الرمز\nBarcode')
        ]
        
        # Column widths (RTL)
        col_widths = [60, 55, 45, 60, 55, 40, 40, 120, 50]
        
        # Draw header row
        c.setFont(font_name, 8)
        c.setFillColor(colors.Color(0.9, 0.9, 0.9))
        c.rect(self.MARGIN, y - 30, self.PAGE_WIDTH - 2*self.MARGIN, 30, fill=True)
        c.setFillColor(colors.black)
        
        x = self.PAGE_WIDTH - self.MARGIN
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            c.drawRightString(x - 5, y - 12, header.split('\n')[0])
            c.drawRightString(x - 5, y - 22, header.split('\n')[1] if '\n' in header else '')
            x -= width
        
        # Draw items
        y -= 35
        c.setFont(font_name, 9)
        
        for item in items:
            x = self.PAGE_WIDTH - self.MARGIN
            
            row_data = [
                self.format_number(item.get('net_amount', 0)),
                self.format_number(item.get('tax_amount', 0)),
                f"{item.get('discount_percent', 0)}%",
                self.format_number(item.get('total_price', 0)),
                self.format_number(item.get('unit_price', 0)),
                str(int(item.get('quantity', 1))),
                self.arabic_text(translate_unit(item.get('unit', ''), lang) or translate_unit('piece', lang)),
                self.arabic_text(item.get('item_name', '')),
                item.get('item_barcode', '')
            ]
            
            for value, width in zip(row_data, col_widths):
                c.drawRightString(x - 5, y, str(value))
                x -= width
            
            y -= 18
            
            # Draw row line
            c.setStrokeColor(colors.lightgrey)
            c.line(self.MARGIN, y + 5, self.PAGE_WIDTH - self.MARGIN, y + 5)
        
        return y
    
    def _draw_totals_and_qr(self, c: canvas.Canvas, invoice: dict, 
                            settings: dict, font_name: str):
        """Draw totals section and QR code"""
        y = self.PAGE_HEIGHT - 450
        
        # Left side: Totals
        c.setFont(font_name, 10)
        
        totals = [
            (self.arabic_text('الخصم Discount:'), self.format_number(invoice.get('discount_amount', 0))),
            (self.arabic_text('الاجمالي الخاضع للضريبة Taxable Total:'), 
             self.format_number(invoice.get('taxable_amount', 0))),
            (self.arabic_text('ضريبة 15% TAX 15%:'), self.format_number(invoice.get('tax_amount', 0))),
            (self.arabic_text('الصافي شامل الضريبة Net Including Tax:'), 
             self.format_number(invoice.get('net_total', 0))),
        ]
        
        for label, value in totals:
            c.drawString(self.MARGIN + 10, y, value)
            c.drawRightString(280, y, label)
            y -= 18
        
        # Right side: QR Code
        if QR_AVAILABLE:
            try:
                qr_bytes = generate_invoice_qr(invoice, settings)
                if qr_bytes:
                    qr_buffer = BytesIO(qr_bytes)
                    qr_image = Image(qr_buffer, width=100, height=100)
                    qr_image.drawOn(c, self.PAGE_WIDTH - self.MARGIN - 120, 
                                   self.PAGE_HEIGHT - 530)
            except Exception as e:
                print(f"Error drawing QR code: {e}")
        
        # Recipient info on right
        c.setFont(font_name, 9)
        recipient_y = self.PAGE_HEIGHT - 410
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, recipient_y, 
                         self.arabic_text("المستلم The recipient:"))
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, recipient_y - 30, 
                         self.arabic_text("المرجع REF:"))
        
        # VAT note
        c.setFont(font_name, 8)
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN, self.PAGE_HEIGHT - 540,
                         self.arabic_text("الاسعار تشمل ضريبة القيمة المضافة"))
    
    def _draw_terms(self, c: canvas.Canvas, settings: dict, font_name: str):
        """Draw terms and conditions"""
        y = self.PAGE_HEIGHT - 570
        
        terms = settings.get('terms_conditions', [])
        if isinstance(terms, str):
            try:
                import json
                terms = json.loads(terms)
            except:
                terms = []
        
        c.setFont(font_name, 7)
        
        for i, term in enumerate(terms[:8], 1):  # Limit to 8 terms
            term_text = self.arabic_text(f"{i}- {term}")
            c.drawRightString(self.PAGE_WIDTH - self.MARGIN, y, term_text)
            y -= 12
    
    def _draw_signature(self, c: canvas.Canvas, font_name: str):
        """Draw signature line"""
        y = 50
        
        c.setFont(font_name, 10)
        sig_text = self.arabic_text("توقيع العميل ..........")
        c.drawCentredString(self.PAGE_WIDTH / 2, y, sig_text)


# Singleton instance
_pdf_generator = None

def get_pdf_generator() -> ArabicPDFGenerator:
    """Get PDF generator singleton"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = ArabicPDFGenerator()
    return _pdf_generator


def generate_invoice_pdf(invoice_data: dict, company_settings: dict, 
                        output_path: str = None) -> Optional[bytes]:
    """
    Convenience function to generate invoice PDF
    
    Args:
        invoice_data: Invoice dictionary with items
        company_settings: Company settings dictionary
        output_path: Optional path to save PDF
        
    Returns:
        PDF bytes or None
    """
    generator = get_pdf_generator()
    return generator.generate_invoice_pdf(invoice_data, company_settings, output_path)


if __name__ == "__main__":
    # Test PDF generation
    print("Testing PDF Generator...")
    
    # Sample data
    company = {
        'company_name_ar': 'مؤسسة التفرد الاصيل للمطابخ',
        'address_ar': 'بريدة - طريق الملك فيصل - حي العجيبة',
        'tax_number': '300694858900003',
        'phone1': '0591650315',
        'phone2': '0580911269',
        'terms_conditions': [
            'يدفع الزبون 50% من قيمة الفاتورة خلال توقيع العقد',
            'عند انتهاء المحلات من التصنيع يلتزم الزبون بتسديد كامل المبلغ'
        ]
    }
    
    invoice = {
        'invoice_number': '2024100127',
        'invoice_date': '2025-03-06',
        'invoice_time': '05:37:56',
        'customer_name': 'فهد عبد المطيري',
        'customer_tax_number': '0544054759',
        'customer_phone': '',
        'customer_address': '',
        'payment_type': 'نقدا',
        'salesperson': 'admin',
        'subtotal': 6087.00,
        'discount_amount': 0.00,
        'taxable_amount': 6087.00,
        'tax_amount': 913.05,
        'net_total': 7000.05,
        'items': [
            {
                'item_name': 'مطبخ تفصيل المنيوم',
                'item_barcode': '',
                'unit': 'حبة',
                'quantity': 1,
                'unit_price': 6087.00,
                'total_price': 6087.00,
                'discount_percent': 0,
                'tax_amount': 913.05,
                'net_amount': 7000.05
            }
        ]
    }
    
    if PDF_AVAILABLE:
        generator = ArabicPDFGenerator()
        pdf_bytes = generator.generate_invoice_pdf(invoice, company, 'test_invoice.pdf')
        print("PDF generated: test_invoice.pdf")
    else:
        print("ReportLab not installed")
