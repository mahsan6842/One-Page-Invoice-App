"""
Invoice Application - Create/Edit Invoice Screen
Main form for creating and editing invoices
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from app.database import get_database
from app.invoice_logic import InvoiceCalculator, InvoiceValidator, format_saudi_number
from ui.widgets import (
    ArabicEntry, ArabicLabel, NumberEntry, LabeledEntry,
    FormSection, AutocompleteEntry
)


class InvoiceItemRow(ttk.Frame):
    """Single row in items list"""
    
    def __init__(self, parent, on_change: Callable = None, 
                 on_delete: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_change = on_change
        self.on_delete = on_delete
        self.vat_rate = 0.15
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Item name
        self.item_name = ArabicEntry(self, width=25)
        self.item_name.pack(side='right', padx=2)
        self.item_name.bind('<KeyRelease>', self._on_value_change)
        
        # Unit dropdown
        self.unit_var = tk.StringVar(value='حبة')
        self.unit = ttk.Combobox(self, textvariable=self.unit_var, 
                                 values=['حبة', 'متر', 'كيلو', 'قطعة', 'علبة'],
                                 width=6, justify='center')
        self.unit.pack(side='right', padx=2)
        
        # Quantity
        self.quantity = NumberEntry(self, width=6)
        self.quantity.insert(0, '1')
        self.quantity.pack(side='right', padx=2)
        self.quantity.bind('<KeyRelease>', self._on_value_change)
        
        # Unit price
        self.unit_price = NumberEntry(self, width=10)
        self.unit_price.insert(0, '0')
        self.unit_price.pack(side='right', padx=2)
        self.unit_price.bind('<KeyRelease>', self._on_value_change)
        
        # Total (read-only)
        self.total_var = tk.StringVar(value='0.00')
        self.total = ttk.Entry(self, textvariable=self.total_var, 
                              width=10, state='readonly', justify='right')
        self.total.pack(side='right', padx=2)
        
        # Discount %
        self.discount = NumberEntry(self, width=5)
        self.discount.insert(0, '0')
        self.discount.pack(side='right', padx=2)
        self.discount.bind('<KeyRelease>', self._on_value_change)
        
        # Tax (read-only)
        self.tax_var = tk.StringVar(value='0.00')
        self.tax = ttk.Entry(self, textvariable=self.tax_var,
                            width=8, state='readonly', justify='right')
        self.tax.pack(side='right', padx=2)
        
        # Net (read-only)
        self.net_var = tk.StringVar(value='0.00')
        self.net = ttk.Entry(self, textvariable=self.net_var,
                            width=10, state='readonly', justify='right')
        self.net.pack(side='right', padx=2)
        
        # Delete button
        self.delete_btn = ttk.Button(self, text='🗑️', width=3,
                                     command=self._on_delete)
        self.delete_btn.pack(side='right', padx=2)
    
    def _on_value_change(self, event=None):
        self._calculate()
        if self.on_change:
            self.on_change()
    
    def _on_delete(self):
        if self.on_delete:
            self.on_delete(self)
    
    def _calculate(self):
        """Calculate item totals"""
        try:
            qty = float(self.quantity.get() or 0)
            price = float(self.unit_price.get() or 0)
            disc = float(self.discount.get() or 0)
            
            total = qty * price
            disc_amount = total * (disc / 100)
            taxable = total - disc_amount
            tax = taxable * self.vat_rate
            net = taxable + tax
            
            self.total_var.set(f"{total:,.2f}")
            self.tax_var.set(f"{tax:,.2f}")
            self.net_var.set(f"{net:,.2f}")
        except ValueError:
            pass
    
    def get_data(self) -> Dict[str, Any]:
        """Get item data as dictionary"""
        qty = float(self.quantity.get() or 0)
        price = float(self.unit_price.get() or 0)
        disc = float(self.discount.get() or 0)
        
        total = qty * price
        disc_amount = total * (disc / 100)
        taxable = total - disc_amount
        tax = taxable * self.vat_rate
        net = taxable + tax
        
        return {
            'item_name': self.item_name.get(),
            'unit': self.unit_var.get(),
            'quantity': qty,
            'unit_price': price,
            'total_price': round(total, 2),
            'discount_percent': disc,
            'discount_amount': round(disc_amount, 2),
            'tax_amount': round(tax, 2),
            'net_amount': round(net, 2)
        }
    
    def set_data(self, data: Dict[str, Any]):
        """Set item data from dictionary"""
        self.item_name.delete(0, tk.END)
        self.item_name.insert(0, data.get('item_name', ''))
        
        self.unit_var.set(data.get('unit', 'حبة'))
        
        self.quantity.delete(0, tk.END)
        self.quantity.insert(0, str(data.get('quantity', 1)))
        
        self.unit_price.delete(0, tk.END)
        self.unit_price.insert(0, str(data.get('unit_price', 0)))
        
        self.discount.delete(0, tk.END)
        self.discount.insert(0, str(data.get('discount_percent', 0)))
        
        self._calculate()


class InvoiceForm(ttk.Frame):
    """Invoice creation/editing form"""
    
    def __init__(self, parent, on_save: Callable = None, 
                 on_save_print: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_save_callback = on_save
        self.on_save_print_callback = on_save_print
        self.db = get_database()
        self.calculator = InvoiceCalculator()
        self.item_rows: List[InvoiceItemRow] = []
        self.editing_invoice_id = None
        self.vat_rate = 15.0  # Default VAT rate until settings loaded
        
        self._create_widgets()
        self._load_settings()
    
    def _create_widgets(self):
        # Main container with scrollbar
        main_canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=main_canvas.yview)
        
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox('all'))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='left', fill='y')
        main_canvas.pack(side='right', fill='both', expand=True)
        
        # Bind mouse wheel
        main_canvas.bind_all('<MouseWheel>', 
                            lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))
        
        # === Customer Section ===
        customer_frame = FormSection(self.scrollable_frame, "معلومات العميل")
        customer_frame.pack(fill='x', padx=10, pady=5)
        
        # Row 1: Name and Tax Number
        row1 = ttk.Frame(customer_frame)
        row1.pack(fill='x', pady=2)
        
        # Tax number (left side)
        ttk.Label(row1, text="الرقم الضريبي:").pack(side='right', padx=5)
        self.customer_tax = ArabicEntry(row1, width=20)
        self.customer_tax.pack(side='right', padx=5)
        
        ttk.Label(row1, text="   ").pack(side='right')  # Spacer
        
        # Customer name (right side)
        ttk.Label(row1, text="اسم العميل:").pack(side='right', padx=5)
        self.customer_name = ArabicEntry(row1, width=25)
        self.customer_name.pack(side='right', padx=5)
        
        # Row 2: Phone and Address
        row2 = ttk.Frame(customer_frame)
        row2.pack(fill='x', pady=2)
        
        ttk.Label(row2, text="العنوان:").pack(side='right', padx=5)
        self.customer_address = ArabicEntry(row2, width=20)
        self.customer_address.pack(side='right', padx=5)
        
        ttk.Label(row2, text="   ").pack(side='right')
        
        ttk.Label(row2, text="الهاتف:").pack(side='right', padx=5)
        self.customer_phone = ArabicEntry(row2, width=15)
        self.customer_phone.pack(side='right', padx=5)
        
        # === Items Section ===
        items_frame = FormSection(self.scrollable_frame, "الأصناف")
        items_frame.pack(fill='x', padx=10, pady=5)
        
        # Items header
        header_frame = ttk.Frame(items_frame)
        header_frame.pack(fill='x', pady=(0, 5))
        
        headers = [
            ('الصنف', 25), ('الوحدة', 8), ('الكمية', 6), ('السعر', 10),
            ('الإجمالي', 10), ('خصم%', 5), ('الضريبة', 8), ('الصافي', 10), ('', 3)
        ]
        
        for text, width in headers:
            ttk.Label(header_frame, text=text, width=width, anchor='center').pack(side='right', padx=2)
        
        # Items container
        self.items_container = ttk.Frame(items_frame)
        self.items_container.pack(fill='x')
        
        # Add first item row
        self._add_item_row()
        
        # Add item button
        add_btn = ttk.Button(items_frame, text="+ إضافة صنف", command=self._add_item_row)
        add_btn.pack(anchor='e', pady=5)
        
        # === Totals Section ===
        totals_frame = FormSection(self.scrollable_frame, "الإجماليات")
        totals_frame.pack(fill='x', padx=10, pady=5)
        
        # Create totals grid
        totals_grid = ttk.Frame(totals_frame)
        totals_grid.pack(anchor='e')
        
        # Subtotal
        ttk.Label(totals_grid, text="المجموع:").grid(row=0, column=1, sticky='e', padx=5, pady=2)
        self.subtotal_var = tk.StringVar(value='0.00')
        ttk.Entry(totals_grid, textvariable=self.subtotal_var, width=15,
                 state='readonly', justify='right').grid(row=0, column=0, padx=5, pady=2)
        
        # Discount
        ttk.Label(totals_grid, text="الخصم (%):").grid(row=1, column=1, sticky='e', padx=5, pady=2)
        discount_frame = ttk.Frame(totals_grid)
        discount_frame.grid(row=1, column=0, padx=5, pady=2)
        
        self.discount_amount_var = tk.StringVar(value='0.00')
        ttk.Entry(discount_frame, textvariable=self.discount_amount_var, width=10,
                 state='readonly', justify='right').pack(side='left')
        ttk.Label(discount_frame, text=" ← ").pack(side='left')
        self.global_discount = NumberEntry(discount_frame, width=5)
        self.global_discount.insert(0, '0')
        self.global_discount.pack(side='left')
        self.global_discount.bind('<KeyRelease>', lambda e: self._update_totals())
        
        # Separator
        ttk.Separator(totals_grid, orient='horizontal').grid(row=2, column=0, columnspan=2, 
                                                             sticky='ew', pady=5)
        
        # Taxable amount
        ttk.Label(totals_grid, text="الخاضع للضريبة:").grid(row=3, column=1, sticky='e', padx=5, pady=2)
        self.taxable_var = tk.StringVar(value='0.00')
        ttk.Entry(totals_grid, textvariable=self.taxable_var, width=15,
                 state='readonly', justify='right').grid(row=3, column=0, padx=5, pady=2)
        
        # Tax amount
        ttk.Label(totals_grid, text="ضريبة 15%:").grid(row=4, column=1, sticky='e', padx=5, pady=2)
        self.tax_var = tk.StringVar(value='0.00')
        ttk.Entry(totals_grid, textvariable=self.tax_var, width=15,
                 state='readonly', justify='right').grid(row=4, column=0, padx=5, pady=2)
        
        # Net total
        ttk.Label(totals_grid, text="الصافي شامل الضريبة:", 
                 font=('Arial', 10, 'bold')).grid(row=5, column=1, sticky='e', padx=5, pady=5)
        self.net_var = tk.StringVar(value='0.00')
        net_entry = ttk.Entry(totals_grid, textvariable=self.net_var, width=15,
                             state='readonly', justify='right', font=('Arial', 10, 'bold'))
        net_entry.grid(row=5, column=0, padx=5, pady=5)
        
        # === Payment Section ===
        payment_frame = ttk.Frame(self.scrollable_frame)
        payment_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(payment_frame, text="نوع الدفع:").pack(side='right', padx=5)
        
        self.payment_var = tk.StringVar(value='نقدا')
        for text in ['نقدا', 'آجل', 'تحويل بنكي']:
            ttk.Radiobutton(payment_frame, text=text, variable=self.payment_var,
                           value=text).pack(side='right', padx=10)
        
        # === Buttons ===
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill='x', padx=10, pady=15)
        
        ttk.Button(btn_frame, text="❌ إلغاء", command=self._clear_form,
                  width=15).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="🖨️ حفظ وطباعة", command=self._save_and_print,
                  width=15).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="💾 حفظ", command=self._save,
                  width=15).pack(side='right', padx=5)
    
    def _load_settings(self):
        """Load company settings for VAT rate"""
        settings = self.db.get_company_settings()
        self.vat_rate = settings.get('vat_rate', 0.15)
        self.calculator = InvoiceCalculator(self.vat_rate)
    
    def _add_item_row(self):
        """Add new item row"""
        row = InvoiceItemRow(self.items_container, 
                            on_change=self._update_totals,
                            on_delete=self._delete_item_row)
        row.vat_rate = self.vat_rate
        row.pack(fill='x', pady=2)
        self.item_rows.append(row)
    
    def _delete_item_row(self, row: InvoiceItemRow):
        """Delete item row"""
        if len(self.item_rows) > 1:
            row.destroy()
            self.item_rows.remove(row)
            self._update_totals()
        else:
            messagebox.showwarning("تنبيه", "يجب أن تحتوي الفاتورة على صنف واحد على الأقل")
    
    def _update_totals(self):
        """Recalculate invoice totals"""
        # Get all items data
        items = [row.get_data() for row in self.item_rows]
        
        # Calculate
        global_discount = float(self.global_discount.get() or 0)
        result = self.calculator.calculate_invoice(items, global_discount)
        
        # Update display
        self.subtotal_var.set(f"{result['subtotal']:,.2f}")
        self.discount_amount_var.set(f"{result['discount_amount']:,.2f}")
        self.taxable_var.set(f"{result['taxable_amount']:,.2f}")
        self.tax_var.set(f"{result['tax_amount']:,.2f}")
        self.net_var.set(f"{result['net_total']:,.2f}")
    
    def _get_invoice_data(self) -> Dict[str, Any]:
        """Collect all form data"""
        items = [row.get_data() for row in self.item_rows]
        global_discount = float(self.global_discount.get() or 0)
        result = self.calculator.calculate_invoice(items, global_discount)
        
        return {
            'customer_name': self.customer_name.get(),
            'customer_tax_number': self.customer_tax.get(),
            'customer_phone': self.customer_phone.get(),
            'customer_address': self.customer_address.get(),
            'payment_type': self.payment_var.get(),
            'salesperson': 'admin',
            'subtotal': result['subtotal'],
            'discount_percent': global_discount,
            'discount_amount': result['discount_amount'],
            'taxable_amount': result['taxable_amount'],
            'tax_amount': result['tax_amount'],
            'net_total': result['net_total'],
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'invoice_time': datetime.now().strftime('%H:%M:%S'),
            'items': result['items']
        }
    
    def _validate(self) -> bool:
        """Validate form data"""
        invoice_data = self._get_invoice_data()
        
        # Check items
        if not invoice_data['items'] or all(not item['item_name'].strip() 
                                            for item in invoice_data['items']):
            messagebox.showerror("خطأ", "يرجى إضافة صنف واحد على الأقل")
            return False
        
        # Validate each item
        for i, item in enumerate(invoice_data['items'], 1):
            if item['item_name'].strip():
                if item['quantity'] <= 0:
                    messagebox.showerror("خطأ", f"الصنف {i}: الكمية يجب أن تكون أكبر من صفر")
                    return False
                if item['unit_price'] < 0:
                    messagebox.showerror("خطأ", f"الصنف {i}: السعر لا يمكن أن يكون سالباً")
                    return False
        
        return True
    
    def _save(self):
        """Save invoice"""
        if not self._validate():
            return
        
        invoice_data = self._get_invoice_data()
        
        # Filter out empty items
        invoice_data['items'] = [item for item in invoice_data['items'] 
                                 if item['item_name'].strip()]
        
        try:
            # Create invoice in database
            invoice_id = self.db.create_invoice(invoice_data, invoice_data['items'])
            
            # Get the created invoice with number
            invoice = self.db.get_invoice(invoice_id)
            
            messagebox.showinfo("نجاح", 
                              f"تم حفظ الفاتورة رقم {invoice['invoice_number']}")
            
            if self.on_save_callback:
                self.on_save_callback(invoice)
            
            self._clear_form()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")
    
    def _save_and_print(self):
        """Save and print invoice"""
        if not self._validate():
            return
        
        invoice_data = self._get_invoice_data()
        invoice_data['items'] = [item for item in invoice_data['items'] 
                                 if item['item_name'].strip()]
        
        try:
            invoice_id = self.db.create_invoice(invoice_data, invoice_data['items'])
            invoice = self.db.get_invoice(invoice_id)
            
            if self.on_save_print_callback:
                self.on_save_print_callback(invoice)
            
            self._clear_form()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def _clear_form(self):
        """Reset form to initial state"""
        # Clear customer info
        self.customer_name.delete(0, tk.END)
        self.customer_tax.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)
        self.customer_address.delete(0, tk.END)
        
        # Clear items
        for row in self.item_rows[1:]:
            row.destroy()
        self.item_rows = [self.item_rows[0]]
        
        # Reset first row
        self.item_rows[0].item_name.delete(0, tk.END)
        self.item_rows[0].quantity.delete(0, tk.END)
        self.item_rows[0].quantity.insert(0, '1')
        self.item_rows[0].unit_price.delete(0, tk.END)
        self.item_rows[0].unit_price.insert(0, '0')
        self.item_rows[0].discount.delete(0, tk.END)
        self.item_rows[0].discount.insert(0, '0')
        self.item_rows[0].unit_var.set('حبة')
        
        # Reset discount and payment
        self.global_discount.delete(0, tk.END)
        self.global_discount.insert(0, '0')
        self.payment_var.set('نقدا')
        
        # Update totals
        self._update_totals()
        
        self.editing_invoice_id = None
    
    def load_invoice(self, invoice: Dict[str, Any]):
        """Load invoice for editing"""
        self._clear_form()
        
        self.editing_invoice_id = invoice.get('id')
        
        # Load customer info
        self.customer_name.insert(0, invoice.get('customer_name', ''))
        self.customer_tax.insert(0, invoice.get('customer_tax_number', ''))
        self.customer_phone.insert(0, invoice.get('customer_phone', ''))
        self.customer_address.insert(0, invoice.get('customer_address', ''))
        
        # Load payment type
        self.payment_var.set(invoice.get('payment_type', 'نقدا'))
        
        # Load discount
        self.global_discount.delete(0, tk.END)
        self.global_discount.insert(0, str(invoice.get('discount_percent', 0)))
        
        # Load items
        items = invoice.get('items', [])
        for i, item in enumerate(items):
            if i >= len(self.item_rows):
                self._add_item_row()
            self.item_rows[i].set_data(item)
        
        self._update_totals()
