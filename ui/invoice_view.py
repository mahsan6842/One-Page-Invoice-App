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
from app.i18n import LANG_AR, LANG_EN, t, translate_payment_type
from app.pdf_generator import generate_invoice_pdf, PDF_AVAILABLE


class InvoiceView(tk.Toplevel):
    """Invoice preview and print dialog"""
    
    def __init__(self, parent, invoice: Dict[str, Any], 
                 print_mode: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.invoice = invoice
        self.db = get_database()
        self.company_settings = self.db.get_company_settings()
        self.lang = self.company_settings.get("ui_language", LANG_AR) or LANG_AR
        self.pdf_path = None
        
        self.title(t("view.invoiceTitle", self.lang, number=invoice.get('invoice_number', '')))
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
        
        self.header_label = ttk.Label(
            header_frame,
            text=t("view.header", self.lang, number=self.invoice.get('invoice_number', '')),
            font=('Arial', 14, 'bold')
        )
        self.header_label.pack(side='right')
        
        self.close_btn = ttk.Button(header_frame, text=t("common.close", self.lang), command=self.destroy)
        self.close_btn.pack(side='left')
        
        # Invoice details frame
        self.details_frame = ttk.LabelFrame(self, text=t("view.detailsGroup", self.lang), padding=10)
        self.details_frame.pack(fill='x', padx=10, pady=5)
        
        # Invoice info
        info_grid = ttk.Frame(self.details_frame)
        info_grid.pack(fill='x')
        
        info_data = [
            (t("view.label.date", self.lang), self.invoice.get('invoice_date', '')),
            (t("view.label.time", self.lang), self.invoice.get('invoice_time', '')),
            (t("view.label.customer", self.lang), self.invoice.get('customer_name', '-') or '-'),
            (t("view.label.payment", self.lang), translate_payment_type(self.invoice.get('payment_type', ''), self.lang)),
        ]
        
        self.info_label_widgets = []
        for i, (label, value) in enumerate(info_data):
            lbl = ttk.Label(info_grid, text=label, font=('Arial', 10, 'bold'))
            lbl.grid(
                row=i, column=1, sticky='e', padx=5, pady=2)
            val = ttk.Label(info_grid, text=value)
            val.grid(
                row=i, column=0, sticky='e', padx=5, pady=2)
            self.info_label_widgets.append((lbl, val))
        
        # Items table
        self.items_frame = ttk.LabelFrame(self, text=t("view.itemsGroup", self.lang), padding=10)
        self.items_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create items table
        columns = ('item', 'qty', 'price', 'total', 'tax', 'net')
        self.tree = ttk.Treeview(self.items_frame, columns=columns, show='headings', height=8)
        
        self.tree.heading('item', text=t("view.col.item", self.lang))
        self.tree.heading('qty', text=t("view.col.qty", self.lang))
        self.tree.heading('price', text=t("view.col.price", self.lang))
        self.tree.heading('total', text=t("view.col.total", self.lang))
        self.tree.heading('tax', text=t("view.col.tax", self.lang))
        self.tree.heading('net', text=t("view.col.net", self.lang))
        
        self.tree.column('item', width=150, anchor='e')
        self.tree.column('qty', width=60, anchor='center')
        self.tree.column('price', width=80, anchor='e')
        self.tree.column('total', width=80, anchor='e')
        self.tree.column('tax', width=70, anchor='e')
        self.tree.column('net', width=90, anchor='e')
        
        # Insert items
        for item in self.invoice.get('items', []):
            self.tree.insert('', tk.END, values=(
                item.get('item_name', ''),
                item.get('quantity', 0),
                f"{item.get('unit_price', 0):,.2f}",
                f"{item.get('total_price', 0):,.2f}",
                f"{item.get('tax_amount', 0):,.2f}",
                f"{item.get('net_amount', 0):,.2f}"
            ))
        
        self.tree.pack(fill='both', expand=True)
        
        # Totals frame
        self.totals_frame = ttk.LabelFrame(self, text=t("view.totalsGroup", self.lang), padding=10)
        self.totals_frame.pack(fill='x', padx=10, pady=5)
        
        totals_grid = ttk.Frame(self.totals_frame)
        totals_grid.pack(anchor='e')
        
        totals_data = [
            (t("view.total.subtotal", self.lang), f"{self.invoice.get('subtotal', 0):,.2f}"),
            (t("view.total.discount", self.lang), f"{self.invoice.get('discount_amount', 0):,.2f}"),
            (t("view.total.taxable", self.lang), f"{self.invoice.get('taxable_amount', 0):,.2f}"),
            (t("view.total.vat", self.lang), f"{self.invoice.get('tax_amount', 0):,.2f}"),
            (t("view.total.net", self.lang), f"{self.invoice.get('net_total', 0):,.2f}"),
        ]
        
        self.totals_label_widgets = []
        for i, (label, value) in enumerate(totals_data):
            font = ('Arial', 10, 'bold') if i == len(totals_data) - 1 else ('Arial', 10)
            lbl = ttk.Label(totals_grid, text=label, font=font)
            lbl.grid(
                row=i, column=1, sticky='e', padx=5, pady=2)
            currency = "ريال" if self.lang != LANG_EN else "SAR"
            val = ttk.Label(totals_grid, text=f"{value} {currency}", font=font)
            val.grid(
                row=i, column=0, sticky='e', padx=5, pady=2)
            self.totals_label_widgets.append((lbl, val))
        
        # Action buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=15)
        
        self.print_btn = ttk.Button(btn_frame, text=t("view.btn.print", self.lang), command=self._print, width=15)
        self.print_btn.pack(side='right', padx=5)
        self.save_btn = ttk.Button(btn_frame, text=t("view.btn.savePdf", self.lang), command=self._save_pdf, width=15)
        self.save_btn.pack(side='right', padx=5)
        
        # Status label
        self.status_label = ttk.Label(btn_frame, text="")
        self.status_label.pack(side='left', padx=5)
    
    def _generate_pdf(self) -> bool:
        """Generate PDF to temp file"""
        if not PDF_AVAILABLE:
            self.status_label.configure(text=t("view.pdf.missing", self.lang))
            return False
        
        try:
            # Create temp file
            fd, self.pdf_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            
            # Generate PDF
            generate_invoice_pdf(self.invoice, self.company_settings, self.pdf_path)
            
            self.status_label.configure(text=t("view.pdf.generated", self.lang))
            return True
            
        except Exception as e:
            self.status_label.configure(text=f"✗ خطأ: {str(e)}")
            return False
    
    def _print(self):
        """Print the invoice"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            if not self._generate_pdf():
                messagebox.showerror(t("common.error", self.lang), t("view.err.pdfCreate", self.lang))
                return
        
        try:
            # Windows printing
            if os.name == 'nt':
                os.startfile(self.pdf_path, 'print')
                self.status_label.configure(text=t("view.print.sent", self.lang))
            else:
                # Linux/Mac
                subprocess.run(['lpr', self.pdf_path], check=True)
                self.status_label.configure(text=t("view.print.sent", self.lang))
                
        except Exception as e:
            messagebox.showerror(t("common.error", self.lang), t("view.err.print", self.lang, error=str(e)))
    
    def _save_pdf(self):
        """Save PDF to user-selected location"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            if not self._generate_pdf():
                messagebox.showerror(t("common.error", self.lang), t("view.err.pdfCreate", self.lang))
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
                self.status_label.configure(text=t("view.save.done", self.lang))
                messagebox.showinfo(t("common.success", self.lang), t("view.save.success", self.lang, path=filepath))
            except Exception as e:
                messagebox.showerror(t("common.error", self.lang), t("view.err.save", self.lang, error=str(e)))
    
    def destroy(self):
        """Clean up temp file on close"""
        if self.pdf_path and os.path.exists(self.pdf_path):
            try:
                os.remove(self.pdf_path)
            except:
                pass
        super().destroy()
