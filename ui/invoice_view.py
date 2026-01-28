"""
Invoice Application - Invoice View/Print Screen
Preview and print invoice PDF
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import tempfile
import subprocess
from typing import Dict, Any, Optional

from app.database import get_database
from app.pdf_generator import generate_invoice_pdf, PDF_AVAILABLE


class InvoiceView(tk.Toplevel):
    """Invoice preview and print dialog"""
    
    def __init__(self, parent, invoice: Dict[str, Any], 
                 print_mode: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.invoice = invoice
        self.db = get_database()
        self.company_settings = self.db.get_company_settings()
        self.pdf_path = None
        
        self.title(f"فاتورة رقم {invoice.get('invoice_number', '')}")
        self.geometry("600x700")
        self.resizable(True, True)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Generate PDF
        self._generate_pdf()
        
        # Auto-print if requested
        if print_mode:
            self.after(500, self._print)
    
    def _create_widgets(self):
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text=f"فاتورة رقم: {self.invoice.get('invoice_number', '')}",
                 font=('Arial', 14, 'bold')).pack(side='right')
        
        ttk.Button(header_frame, text="✖️ إغلاق", command=self.destroy).pack(side='left')
        
        # Invoice details frame
        details_frame = ttk.LabelFrame(self, text="تفاصيل الفاتورة", padding=10)
        details_frame.pack(fill='x', padx=10, pady=5)
        
        # Invoice info
        info_grid = ttk.Frame(details_frame)
        info_grid.pack(fill='x')
        
        info_data = [
            ('التاريخ:', self.invoice.get('invoice_date', '')),
            ('الوقت:', self.invoice.get('invoice_time', '')),
            ('العميل:', self.invoice.get('customer_name', '-')),
            ('نوع الدفع:', self.invoice.get('payment_type', '')),
        ]
        
        for i, (label, value) in enumerate(info_data):
            ttk.Label(info_grid, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=1, sticky='e', padx=5, pady=2)
            ttk.Label(info_grid, text=value).grid(
                row=i, column=0, sticky='e', padx=5, pady=2)
        
        # Items table
        items_frame = ttk.LabelFrame(self, text="الأصناف", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create items table
        columns = ('item', 'qty', 'price', 'total', 'tax', 'net')
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=8)
        
        tree.heading('item', text='الصنف')
        tree.heading('qty', text='الكمية')
        tree.heading('price', text='السعر')
        tree.heading('total', text='الإجمالي')
        tree.heading('tax', text='الضريبة')
        tree.heading('net', text='الصافي')
        
        tree.column('item', width=150, anchor='e')
        tree.column('qty', width=60, anchor='center')
        tree.column('price', width=80, anchor='e')
        tree.column('total', width=80, anchor='e')
        tree.column('tax', width=70, anchor='e')
        tree.column('net', width=90, anchor='e')
        
        # Insert items
        for item in self.invoice.get('items', []):
            tree.insert('', tk.END, values=(
                item.get('item_name', ''),
                item.get('quantity', 0),
                f"{item.get('unit_price', 0):,.2f}",
                f"{item.get('total_price', 0):,.2f}",
                f"{item.get('tax_amount', 0):,.2f}",
                f"{item.get('net_amount', 0):,.2f}"
            ))
        
        tree.pack(fill='both', expand=True)
        
        # Totals frame
        totals_frame = ttk.LabelFrame(self, text="الإجماليات", padding=10)
        totals_frame.pack(fill='x', padx=10, pady=5)
        
        totals_grid = ttk.Frame(totals_frame)
        totals_grid.pack(anchor='e')
        
        totals_data = [
            ('المجموع:', f"{self.invoice.get('subtotal', 0):,.2f}"),
            ('الخصم:', f"{self.invoice.get('discount_amount', 0):,.2f}"),
            ('الخاضع للضريبة:', f"{self.invoice.get('taxable_amount', 0):,.2f}"),
            ('ضريبة 15%:', f"{self.invoice.get('tax_amount', 0):,.2f}"),
            ('الصافي شامل الضريبة:', f"{self.invoice.get('net_total', 0):,.2f}"),
        ]
        
        for i, (label, value) in enumerate(totals_data):
            font = ('Arial', 10, 'bold') if i == len(totals_data) - 1 else ('Arial', 10)
            ttk.Label(totals_grid, text=label, font=font).grid(
                row=i, column=1, sticky='e', padx=5, pady=2)
            ttk.Label(totals_grid, text=f"{value} ريال", font=font).grid(
                row=i, column=0, sticky='e', padx=5, pady=2)
        
        # Action buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=15)
        
        ttk.Button(btn_frame, text="🖨️ طباعة", command=self._print,
                  width=15).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="💾 حفظ PDF", command=self._save_pdf,
                  width=15).pack(side='right', padx=5)
        
        # Status label
        self.status_label = ttk.Label(btn_frame, text="")
        self.status_label.pack(side='left', padx=5)
    
    def _generate_pdf(self) -> bool:
        """Generate PDF to temp file"""
        if not PDF_AVAILABLE:
            self.status_label.configure(text="⚠️ مكتبة PDF غير مثبتة")
            return False
        
        try:
            # Create temp file
            fd, self.pdf_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            
            # Generate PDF
            generate_invoice_pdf(self.invoice, self.company_settings, self.pdf_path)
            
            self.status_label.configure(text="✓ تم إنشاء PDF")
            return True
            
        except Exception as e:
            self.status_label.configure(text=f"✗ خطأ: {str(e)}")
            return False
    
    def _print(self):
        """Print the invoice"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            if not self._generate_pdf():
                messagebox.showerror("خطأ", "فشل إنشاء ملف PDF")
                return
        
        try:
            # Windows printing
            if os.name == 'nt':
                os.startfile(self.pdf_path, 'print')
                self.status_label.configure(text="✓ تم إرسال للطباعة")
            else:
                # Linux/Mac
                subprocess.run(['lpr', self.pdf_path], check=True)
                self.status_label.configure(text="✓ تم إرسال للطباعة")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"فشلت الطباعة: {str(e)}")
    
    def _save_pdf(self):
        """Save PDF to user-selected location"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            if not self._generate_pdf():
                messagebox.showerror("خطأ", "فشل إنشاء ملف PDF")
                return
        
        # Ask for save location
        default_name = f"invoice_{self.invoice.get('invoice_number', 'unknown')}.pdf"
        filepath = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF files', '*.pdf')],
            initialfile=default_name
        )
        
        if filepath:
            try:
                import shutil
                shutil.copy(self.pdf_path, filepath)
                self.status_label.configure(text=f"✓ تم الحفظ")
                messagebox.showinfo("نجاح", f"تم حفظ الفاتورة في:\n{filepath}")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل الحفظ: {str(e)}")
    
    def destroy(self):
        """Clean up temp file on close"""
        if self.pdf_path and os.path.exists(self.pdf_path):
            try:
                os.remove(self.pdf_path)
            except:
                pass
        super().destroy()
