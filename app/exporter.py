"""
Invoice Application - Export Module
Handles CSV and PDF export functionality for invoice history
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional, Tuple
from io import StringIO

from app.pdf_generator import generate_invoice_pdf, PDF_AVAILABLE
from app.database import get_database
from app.i18n import LANG_EN, translate_payment_type


class InvoiceExporter:
    """
    Handles exporting invoices to CSV and PDF formats.
    Designed for offline use and low-spec hardware.
    """
    
    # CSV column configuration
    CSV_COLUMNS = [
        ('invoice_number', 'رقم الفاتورة'),
        ('invoice_date', 'التاريخ'),
        ('invoice_time', 'الوقت'),
        ('customer_name', 'العميل'),
        ('customer_tax_number', 'الرقم الضريبي للعميل'),
        ('payment_type', 'نوع الدفع'),
        ('subtotal', 'المجموع'),
        ('discount_amount', 'الخصم'),
        ('taxable_amount', 'الخاضع للضريبة'),
        ('tax_amount', 'الضريبة'),
        ('net_total', 'الصافي'),
        ('status', 'الحالة'),
    ]

    CSV_COLUMNS_EN = [
        ('invoice_number', 'Invoice No'),
        ('invoice_date', 'Date'),
        ('invoice_time', 'Time'),
        ('customer_name', 'Customer'),
        ('customer_tax_number', 'Customer Tax No'),
        ('payment_type', 'Payment Type'),
        ('subtotal', 'Subtotal'),
        ('discount_amount', 'Discount'),
        ('taxable_amount', 'Taxable Amount'),
        ('tax_amount', 'Tax Amount'),
        ('net_total', 'Total (incl. VAT)'),
        ('status', 'Status'),
    ]
    
    def __init__(self):
        self.db = get_database()
        self._cancelled = False
    
    def cancel(self):
        """Cancel ongoing export operation"""
        self._cancelled = True
    
    def reset(self):
        """Reset cancel flag for new export"""
        self._cancelled = False
    
    # ==================== CSV Export ====================
    
    def export_to_csv(
        self,
        invoice_ids: List[int],
        output_path: str,
        progress_callback: Callable[[int, int, str], None] = None,
        include_arabic_headers: bool = True,
        lang: str = None,
    ) -> Tuple[bool, str]:
        """
        Export selected invoices to a single CSV file.
        
        Args:
            invoice_ids: List of invoice IDs to export
            output_path: Full path for the output CSV file
            progress_callback: Optional callback(current, total, message)
            include_arabic_headers: Include Arabic column names
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        self.reset()
        en = (lang == LANG_EN)
        
        if not invoice_ids:
            return False, ("No invoices selected for export." if en else "لم يتم تحديد أي فواتير للتصدير")
        
        try:
            # Fetch all invoices
            invoices = []
            total = len(invoice_ids)

            # If English UI, default to English headers unless explicitly overridden
            if en:
                include_arabic_headers = False
            
            for i, inv_id in enumerate(invoice_ids):
                if self._cancelled:
                    return False, ("Export cancelled." if en else "تم إلغاء التصدير")
                
                invoice = self.db.get_invoice(inv_id)
                if invoice:
                    invoices.append(invoice)
                
                if progress_callback:
                    if en:
                        progress_callback(i + 1, total, f"Loading invoice {i + 1} of {total}")
                    else:
                        progress_callback(i + 1, total, f"جاري تحميل الفاتورة {i + 1} من {total}")
            
            if not invoices:
                return False, ("No invoices found to export." if en else "لم يتم العثور على فواتير للتصدير")
            
            # Write CSV file
            if progress_callback:
                progress_callback(total, total, "Writing CSV..." if en else "جاري كتابة ملف CSV...")
            
            self._write_csv(invoices, output_path, include_arabic_headers, lang)
            
            return True, (f"Exported {len(invoices)} invoice(s) successfully." if en else f"تم تصدير {len(invoices)} فاتورة بنجاح")
            
        except PermissionError:
            return False, ("Cannot write to this location. Please choose another." if en else "لا يمكن الكتابة في هذا الموقع. يرجى اختيار موقع آخر")
        except OSError as e:
            if "No space" in str(e) or "disk" in str(e).lower():
                return False, ("Not enough disk space." if en else "المساحة غير كافية على القرص")
            return False, (f"File error: {str(e)}" if en else f"خطأ في الملف: {str(e)}")
        except Exception as e:
            return False, (f"Export error: {str(e)}" if en else f"حدث خطأ أثناء التصدير: {str(e)}")
    
    def _write_csv(self, invoices: List[Dict], output_path: str, 
                   include_arabic_headers: bool, lang: str = None):
        """Write invoices to CSV file with proper encoding for Excel"""
        lang = lang or 'ar'
        
        # Use UTF-8 with BOM for Excel Arabic support
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            
            # Write header row
            if include_arabic_headers:
                headers = [col[1] for col in self.CSV_COLUMNS]  # Arabic names
            else:
                headers = [col[1] for col in self.CSV_COLUMNS_EN]  # English labels
            
            writer.writerow(headers)
            
            # Write data rows
            for invoice in invoices:
                row = []
                for col_key, _ in self.CSV_COLUMNS:
                    value = invoice.get(col_key, '')
                    
                    # Format specific columns
                    if col_key in ('subtotal', 'discount_amount', 'taxable_amount', 
                                   'tax_amount', 'net_total'):
                        value = f"{float(value or 0):.2f}"
                    elif col_key == 'status':
                        value = 'نشطة' if value == 'active' else 'ملغاة' if include_arabic_headers else ('Active' if value == 'active' else 'Cancelled')
                    elif col_key == 'payment_type':
                        value = translate_payment_type(value, lang)
                    elif value is None:
                        value = ''
                    
                    row.append(str(value))
                
                writer.writerow(row)
    
    def get_csv_preview(self, invoice_ids: List[int], max_rows: int = 5) -> str:
        """
        Generate a preview of CSV output.
        
        Args:
            invoice_ids: List of invoice IDs
            max_rows: Maximum rows to preview
            
        Returns:
            CSV preview string
        """
        invoices = []
        for inv_id in invoice_ids[:max_rows]:
            invoice = self.db.get_invoice(inv_id)
            if invoice:
                invoices.append(invoice)
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([col[1] for col in self.CSV_COLUMNS])
        
        # Data rows
        for invoice in invoices:
            row = [str(invoice.get(col[0], '')) for col, _ in self.CSV_COLUMNS]
            writer.writerow(row)
        
        if len(invoice_ids) > max_rows:
            output.write(f"\n... و {len(invoice_ids) - max_rows} فواتير أخرى")
        
        return output.getvalue()
    
    # ==================== PDF Export ====================
    
    def export_to_pdf(
        self,
        invoice_ids: List[int],
        output_folder: str,
        progress_callback: Callable[[int, int, str], None] = None,
        filename_pattern: str = "Invoice_{number}.pdf",
        lang: str = None,
    ) -> Tuple[int, int, List[str]]:
        """
        Export selected invoices to individual PDF files.
        
        Args:
            invoice_ids: List of invoice IDs to export
            output_folder: Directory to save PDF files
            progress_callback: Optional callback(current, total, message)
            filename_pattern: Pattern for filenames, {number} is replaced
            
        Returns:
            Tuple of (success_count, total_count, list of error messages)
        """
        self.reset()
        en = (lang == LANG_EN)
        
        if not invoice_ids:
            return 0, 0, ["No invoices selected for export." if en else "لم يتم تحديد أي فواتير للتصدير"]
        
        if not PDF_AVAILABLE:
            return 0, len(invoice_ids), ["PDF library not available. Please install reportlab." if en else "مكتبة PDF غير متوفرة. يرجى تثبيت reportlab"]
        
        # Ensure output folder exists
        try:
            os.makedirs(output_folder, exist_ok=True)
        except PermissionError:
            return 0, len(invoice_ids), ["Cannot create folder. Check permissions." if en else "لا يمكن إنشاء المجلد. تحقق من الصلاحيات"]
        except Exception as e:
            return 0, len(invoice_ids), [f"Folder creation error: {str(e)}" if en else f"خطأ في إنشاء المجلد: {str(e)}"]
        
        # Get company settings once
        company_settings = self.db.get_company_settings()
        
        success_count = 0
        errors = []
        total = len(invoice_ids)
        
        for i, inv_id in enumerate(invoice_ids):
            if self._cancelled:
                errors.append("Export cancelled." if en else "تم إلغاء التصدير")
                break
            
            try:
                # Fetch invoice
                invoice = self.db.get_invoice(inv_id)
                if not invoice:
                    errors.append(f"Invoice {inv_id} not found" if en else f"الفاتورة {inv_id} غير موجودة")
                    continue
                
                # Generate filename
                invoice_number = invoice.get('invoice_number', str(inv_id))
                filename = filename_pattern.replace("{number}", invoice_number)
                filepath = os.path.join(output_folder, filename)
                
                # Update progress
                if progress_callback:
                    progress_callback(i + 1, total, f"Generating {filename}" if en else f"جاري إنشاء {filename}")
                
                # Generate PDF
                generate_invoice_pdf(invoice, company_settings, filepath)
                
                success_count += 1
                
            except PermissionError:
                errors.append(f"Cannot write invoice {invoice_number}" if en else f"لا يمكن كتابة الفاتورة {invoice_number}")
            except Exception as e:
                errors.append(f"Invoice {invoice_number} error: {str(e)}" if en else f"خطأ في الفاتورة {invoice_number}: {str(e)}")
        
        return success_count, total, errors
    
    # ==================== Utility Methods ====================
    
    def get_default_csv_filename(self) -> str:
        """Generate default CSV filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"invoices_export_{timestamp}.csv"
    
    def get_default_pdf_folder(self) -> str:
        """Get default folder for PDF exports"""
        # Use Documents folder or app's output folder
        documents = os.path.expanduser("~/Documents")
        if os.path.exists(documents):
            export_folder = os.path.join(documents, "Invoice_Exports")
        else:
            # Fallback to app's output folder
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            export_folder = os.path.join(app_dir, "output", "exports")
        
        return export_folder
    
    def validate_export_path(self, path: str, is_file: bool = True) -> Tuple[bool, str]:
        """
        Validate export path for permissions and existence.
        
        Args:
            path: Path to validate
            is_file: True if path is a file, False if directory
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if is_file:
                # Check if parent directory exists and is writable
                parent_dir = os.path.dirname(path)
                if not parent_dir:
                    parent_dir = "."
                
                if not os.path.exists(parent_dir):
                    return False, "المجلد غير موجود"
                
                # Test write permission
                test_file = os.path.join(parent_dir, ".write_test")
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                except:
                    return False, "لا توجد صلاحية للكتابة في هذا المجلد"
            else:
                # Directory path
                if os.path.exists(path) and not os.path.isdir(path):
                    return False, "المسار ليس مجلداً"
                
                # Try to create directory
                os.makedirs(path, exist_ok=True)
            
            return True, ""
            
        except PermissionError:
            return False, "لا توجد صلاحية للوصول"
        except Exception as e:
            return False, str(e)
    
    def estimate_export_time(self, count: int, export_type: str) -> str:
        """
        Estimate export time for user feedback.
        
        Args:
            count: Number of invoices
            export_type: 'csv' or 'pdf'
            
        Returns:
            Human-readable time estimate in Arabic
        """
        if export_type == 'csv':
            # CSV is very fast
            if count < 100:
                return "أقل من ثانية"
            elif count < 1000:
                return "بضع ثواني"
            else:
                return f"حوالي {count // 500} ثواني"
        else:
            # PDF takes ~2 seconds per invoice
            seconds = count * 2
            if seconds < 60:
                return f"حوالي {seconds} ثانية"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"حوالي {minutes} دقيقة"
            else:
                hours = seconds // 3600
                return f"حوالي {hours} ساعة"


# Singleton instance
_exporter_instance = None

def get_exporter() -> InvoiceExporter:
    """Get exporter singleton instance"""
    global _exporter_instance
    if _exporter_instance is None:
        _exporter_instance = InvoiceExporter()
    return _exporter_instance


# ==================== Convenience Functions ====================

def export_invoices_to_csv(invoice_ids: List[int], output_path: str,
                           progress_callback: Callable = None) -> Tuple[bool, str]:
    """Quick CSV export function"""
    exporter = get_exporter()
    return exporter.export_to_csv(invoice_ids, output_path, progress_callback)


def export_invoices_to_pdf(invoice_ids: List[int], output_folder: str,
                           progress_callback: Callable = None) -> Tuple[int, int, List[str]]:
    """Quick PDF export function"""
    exporter = get_exporter()
    return exporter.export_to_pdf(invoice_ids, output_folder, progress_callback)


if __name__ == "__main__":
    # Test export functionality
    print("Testing Invoice Exporter...")
    
    exporter = InvoiceExporter()
    
    # Test CSV filename
    print(f"Default CSV filename: {exporter.get_default_csv_filename()}")
    
    # Test time estimates
    print(f"CSV estimate (100): {exporter.estimate_export_time(100, 'csv')}")
    print(f"PDF estimate (10): {exporter.estimate_export_time(10, 'pdf')}")
    print(f"PDF estimate (100): {exporter.estimate_export_time(100, 'pdf')}")
