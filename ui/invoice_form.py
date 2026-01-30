"""
Invoice Application - Create/Edit Invoice Screen
Main form for creating and editing invoices
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from app.database import get_database
from app.i18n import (
    LANG_AR, LANG_EN, t, translate_payment_type, get_current_lang,
    get_unit_display_values, translate_unit, payment_type_to_storage,
    pack_side, pack_side_opposite, justify_for, grid_column_label, grid_column_value,
    sticky_for, pack_anchor_for
)
from app.invoice_logic import InvoiceCalculator, InvoiceValidator, format_saudi_number
from ui.widgets import (
    ArabicEntry, ArabicLabel, NumberEntry, LabeledEntry,
    FormSection, AutocompleteEntry, apply_direction_recursive
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
        lang = get_current_lang() or LANG_AR
        ps = pack_side(lang)
        jf = justify_for(lang)
        self.item_name = ArabicEntry(self, width=25)
        self.item_name.pack(side=ps, padx=2)
        self.item_name.bind('<KeyRelease>', self._on_value_change)
        
        # Unit dropdown - use current language for initial values
        lang = get_current_lang() or LANG_AR
        unit_values = get_unit_display_values(lang)
        self.unit_var = tk.StringVar(value=unit_values[0])
        self.unit = ttk.Combobox(self, textvariable=self.unit_var, 
                                 values=unit_values, width=6, justify='center')
        self.unit.pack(side=ps, padx=2)
        self.quantity = NumberEntry(self, width=6)
        self.quantity.insert(0, '1')
        self.quantity.pack(side=ps, padx=2)
        self.quantity.bind('<KeyRelease>', self._on_value_change)
        
        # Unit price
        self.unit_price = NumberEntry(self, width=10)
        self.unit_price.insert(0, '0')
        self.unit_price.pack(side=ps, padx=2)
        self.unit_price.bind('<KeyRelease>', self._on_value_change)
        
        self.total_var = tk.StringVar(value='0.00')
        self.total = ttk.Entry(self, textvariable=self.total_var, 
                              width=10, state='readonly', justify=jf)
        self.total.pack(side=ps, padx=2)
        self.discount = NumberEntry(self, width=5)
        self.discount.insert(0, '0')
        self.discount.pack(side=ps, padx=2)
        self.discount.bind('<KeyRelease>', self._on_value_change)
        
        self.tax_var = tk.StringVar(value='0.00')
        self.tax = ttk.Entry(self, textvariable=self.tax_var,
                            width=8, state='readonly', justify=jf)
        self.tax.pack(side=ps, padx=2)
        self.net_var = tk.StringVar(value='0.00')
        self.net = ttk.Entry(self, textvariable=self.net_var,
                            width=10, state='readonly', justify=jf)
        self.net.pack(side=ps, padx=2)
        self.delete_btn = ttk.Button(self, text='🗑️', width=3,
                                     command=self._on_delete)
        self.delete_btn.pack(side=ps, padx=2)
    
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
    
    def apply_language(self, lang: str):
        """Update unit dropdown and repack/reconfigure for language direction."""
        lang = lang or LANG_AR
        ps = pack_side(lang)
        jf = justify_for(lang)
        current_val = self.unit_var.get()
        new_values = get_unit_display_values(lang)
        self.unit['values'] = new_values
        translated = translate_unit(current_val, lang)
        if translated in new_values:
            self.unit_var.set(translated)
        elif new_values:
            self.unit_var.set(new_values[0])
        for w in [self.item_name, self.unit, self.quantity, self.unit_price, self.total,
                  self.discount, self.tax, self.net, self.delete_btn]:
            w.pack_forget()
        self.item_name.pack(side=ps, padx=2)
        self.unit.pack(side=ps, padx=2)
        self.quantity.pack(side=ps, padx=2)
        self.unit_price.pack(side=ps, padx=2)
        self.total.configure(justify=jf)
        self.total.pack(side=ps, padx=2)
        self.discount.pack(side=ps, padx=2)
        self.tax.configure(justify=jf)
        self.tax.pack(side=ps, padx=2)
        self.net.configure(justify=jf)
        self.net.pack(side=ps, padx=2)
        self.delete_btn.pack(side=ps, padx=2)
    
    def set_data(self, data: Dict[str, Any]):
        """Set item data from dictionary"""
        self.item_name.delete(0, tk.END)
        self.item_name.insert(0, data.get('item_name', ''))
        
        unit_val = data.get('unit', '')
        lang = get_current_lang() or LANG_AR
        values = get_unit_display_values(lang)
        if unit_val:
            translated = translate_unit(unit_val, lang)
            self.unit_var.set(translated if translated in values else values[0])
        else:
            self.unit_var.set(values[0])
        
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
        self.lang = get_current_lang() or LANG_AR
        
        self._create_widgets()
        self._load_settings()
    
    def _create_widgets(self):
        ps, pso = pack_side(self.lang), pack_side_opposite(self.lang)
        jf = justify_for(self.lang)
        self.main_canvas = tk.Canvas(self, highlightthickness=0)
        self.form_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.main_canvas.yview)
        main_canvas = self.main_canvas
        scrollbar = self.form_scrollbar
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox('all'))
        )
        
        self.canvas_window_id = main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.bind('<Configure>', self._on_canvas_configure)
        scrollbar.pack(side=pso, fill='y')
        main_canvas.pack(side=ps, fill='both', expand=True)
        
        # Bind mouse wheel
        main_canvas.bind_all('<MouseWheel>', 
                            lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))
        
        # === Customer Section ===
        self.customer_frame = FormSection(self.scrollable_frame, "معلومات العميل")
        self.customer_frame.pack(fill='x', padx=10, pady=5)
        
        row1 = ttk.Frame(self.customer_frame)
        row1.pack(fill='x', pady=2)
        self.customer_row1 = row1
        self.lbl_customer_tax = ttk.Label(row1, text="الرقم الضريبي:")
        self.lbl_customer_tax.pack(side=ps, padx=5)
        self.customer_tax = ArabicEntry(row1, width=20)
        self.customer_tax.pack(side=ps, padx=5)
        self.spacer1 = ttk.Label(row1, text="   ")
        self.spacer1.pack(side=ps)
        self.lbl_customer_name = ttk.Label(row1, text="اسم العميل:")
        self.lbl_customer_name.pack(side=ps, padx=5)
        self.customer_name = ArabicEntry(row1, width=25)
        self.customer_name.pack(side=ps, padx=5)
        row2 = ttk.Frame(self.customer_frame)
        row2.pack(fill='x', pady=2)
        self.customer_row2 = row2
        self.lbl_customer_address = ttk.Label(row2, text="العنوان:")
        self.lbl_customer_address.pack(side=ps, padx=5)
        self.customer_address = ArabicEntry(row2, width=20)
        self.customer_address.pack(side=ps, padx=5)
        self.spacer2 = ttk.Label(row2, text="   ")
        self.spacer2.pack(side=ps)
        self.lbl_customer_phone = ttk.Label(row2, text="الهاتف:")
        self.lbl_customer_phone.pack(side=ps, padx=5)
        self.customer_phone = ArabicEntry(row2, width=15)
        self.customer_phone.pack(side=ps, padx=5)
        
        # === Items Section ===
        self.items_frame = FormSection(self.scrollable_frame, "الأصناف")
        self.items_frame.pack(fill='x', padx=10, pady=5)
        
        # Items header
        header_frame = ttk.Frame(self.items_frame)
        header_frame.pack(fill='x', pady=(0, 5))
        
        self._item_header_spec = [
            ("الصنف", 25),
            ("الوحدة", 8),
            ("الكمية", 6),
            ("السعر", 10),
            ("الإجمالي", 10),
            ("خصم%", 5),
            ("الضريبة", 8),
            ("الصافي", 10),
            ("", 3),
        ]
        self.item_header_labels = []
        for text, width in self._item_header_spec:
            lbl = ttk.Label(header_frame, text=text, width=width, anchor='center')
            lbl.pack(side=ps, padx=2)
            self.item_header_labels.append(lbl)
        
        # Items container
        self.items_container = ttk.Frame(self.items_frame)
        self.items_container.pack(fill='x')
        
        # Add first item row
        self._add_item_row()
        
        # Add item button
        self.add_item_btn = ttk.Button(self.items_frame, text="+ إضافة صنف", command=self._add_item_row)
        self.add_item_btn.pack(anchor=pack_anchor_for(self.lang), pady=5)
        
        # === Totals Section ===
        self.totals_frame = FormSection(self.scrollable_frame, "الإجماليات")
        self.totals_frame.pack(fill='x', padx=10, pady=5)
        
        totals_grid = ttk.Frame(self.totals_frame)
        self.totals_grid = totals_grid
        gcl, gcv = grid_column_label(self.lang), grid_column_value(self.lang)
        stk = sticky_for(self.lang)
        totals_grid.pack(anchor=pack_anchor_for(self.lang))
        self.lbl_subtotal = ttk.Label(totals_grid, text="المجموع:")
        self.lbl_subtotal.grid(row=0, column=gcl, sticky=stk, padx=5, pady=2)
        self.subtotal_var = tk.StringVar(value='0.00')
        self.subtotal_entry = ttk.Entry(totals_grid, textvariable=self.subtotal_var, width=15,
                 state='readonly', justify=jf)
        self.subtotal_entry.grid(row=0, column=gcv, padx=5, pady=2)
        self.lbl_discount = ttk.Label(totals_grid, text="الخصم (%):")
        self.lbl_discount.grid(row=1, column=gcl, sticky=stk, padx=5, pady=2)
        discount_frame = ttk.Frame(totals_grid)
        self.discount_frame = discount_frame
        discount_frame.grid(row=1, column=gcv, padx=5, pady=2)
        self.discount_amount_var = tk.StringVar(value='0.00')
        self.discount_amount_entry = ttk.Entry(discount_frame, textvariable=self.discount_amount_var, width=10,
                 state='readonly', justify=jf)
        self.discount_amount_entry.pack(side=pso)
        self.lbl_discount_arrow = ttk.Label(discount_frame, text=t("form.discountArrow", self.lang))
        self.lbl_discount_arrow.pack(side=pso)
        self.global_discount = NumberEntry(discount_frame, width=5)
        self.global_discount.insert(0, '0')
        self.global_discount.pack(side=pso)
        self.global_discount.bind('<KeyRelease>', lambda e: self._update_totals())
        ttk.Separator(totals_grid, orient='horizontal').grid(row=2, column=0, columnspan=2, 
                                                             sticky='ew', pady=5)
        self.lbl_taxable = ttk.Label(totals_grid, text="الخاضع للضريبة:")
        self.lbl_taxable.grid(row=3, column=gcl, sticky=stk, padx=5, pady=2)
        self.taxable_var = tk.StringVar(value='0.00')
        self.taxable_entry = ttk.Entry(totals_grid, textvariable=self.taxable_var, width=15,
                 state='readonly', justify=jf)
        self.taxable_entry.grid(row=3, column=gcv, padx=5, pady=2)
        self.lbl_tax = ttk.Label(totals_grid, text="ضريبة 15%:")
        self.lbl_tax.grid(row=4, column=gcl, sticky=stk, padx=5, pady=2)
        self.tax_var = tk.StringVar(value='0.00')
        self.tax_entry = ttk.Entry(totals_grid, textvariable=self.tax_var, width=15,
                 state='readonly', justify=jf)
        self.tax_entry.grid(row=4, column=gcv, padx=5, pady=2)
        self.lbl_net_total = ttk.Label(totals_grid, text="الصافي شامل الضريبة:",
                                       font=('Arial', 10, 'bold'))
        self.lbl_net_total.grid(row=5, column=gcl, sticky=stk, padx=5, pady=5)
        self.net_var = tk.StringVar(value='0.00')
        self.net_entry = ttk.Entry(totals_grid, textvariable=self.net_var, width=15,
                             state='readonly', justify=jf, font=('Arial', 10, 'bold'))
        self.net_entry.grid(row=5, column=gcv, padx=5, pady=5)
        
        self.payment_frame = ttk.Frame(self.scrollable_frame)
        self.payment_frame.pack(fill='x', padx=10, pady=5)
        self.lbl_payment = ttk.Label(self.payment_frame, text="نوع الدفع:")
        self.lbl_payment.pack(side=ps, padx=5)
        self.payment_var = tk.StringVar(value='نقدا')
        self.payment_radios = []
        for value_ar, text_ar in [('نقدا', 'نقدا'), ('آجل', 'آجل'), ('تحويل بنكي', 'تحويل بنكي')]:
            rb = ttk.Radiobutton(self.payment_frame, text=text_ar, variable=self.payment_var, value=value_ar)
            rb.pack(side=ps, padx=10)
            self.payment_radios.append(rb)
        self.btn_frame = ttk.Frame(self.scrollable_frame)
        self.btn_frame.pack(fill='x', padx=10, pady=15)
        self.btn_cancel = ttk.Button(self.btn_frame, text="❌ إلغاء", command=self._clear_form, width=15)
        self.btn_cancel.pack(side=ps, padx=5)
        self.btn_save_print = ttk.Button(self.btn_frame, text="🖨️ حفظ وطباعة", command=self._save_and_print, width=15)
        self.btn_save_print.pack(side=ps, padx=5)
        self.btn_save = ttk.Button(self.btn_frame, text="💾 حفظ", command=self._save, width=15)
        self.btn_save.pack(side=ps, padx=5)
    
    def _on_canvas_configure(self, event=None):
        """Resize inner frame when canvas resizes."""
        if event and hasattr(self, 'canvas_window_id'):
            self.main_canvas.itemconfig(self.canvas_window_id, width=event.width)

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
            messagebox.showwarning(t("msg.warning", self.lang), t("msg.minOneItem", self.lang))
    
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
            messagebox.showerror(t("common.error", self.lang), t("msg.addOneItem", self.lang))
            return False
        
        # Validate each item
        for i, item in enumerate(invoice_data['items'], 1):
            if item['item_name'].strip():
                if item['quantity'] <= 0:
                    msg = t("msg.itemQtyPositive", self.lang, i=i)
                    messagebox.showerror(t("common.error", self.lang), msg)
                    return False
                if item['unit_price'] < 0:
                    msg = t("msg.itemPriceNegative", self.lang, i=i)
                    messagebox.showerror(t("common.error", self.lang), msg)
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
            
            messagebox.showinfo(t("common.success", self.lang),
                               t("msg.invoiceSaved", self.lang, number=invoice['invoice_number']))
            
            if self.on_save_callback:
                self.on_save_callback(invoice)
            
            self._clear_form()
            
        except Exception as e:
            msg = t("msg.saveFailed", self.lang, error=str(e))
            messagebox.showerror(t("common.error", self.lang), msg)
    
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
            msg = t("msg.errorOccurred", self.lang, error=str(e))
            messagebox.showerror(t("common.error", self.lang), msg)

    def apply_language(self, lang: str):
        """Apply language to this screen (static labels/buttons)."""
        self.lang = lang or LANG_AR

        # Section titles
        self.customer_frame.configure(text=t("form.customerInfo", self.lang))
        self.items_frame.configure(text=t("form.items", self.lang))
        self.totals_frame.configure(text=t("form.totals", self.lang))

        # Customer labels
        self.lbl_customer_tax.configure(text=t("form.taxNumber", self.lang))
        self.lbl_customer_name.configure(text=t("form.customerName", self.lang))
        self.lbl_customer_address.configure(text=t("form.address", self.lang))
        self.lbl_customer_phone.configure(text=t("form.phone", self.lang))

        # Item header labels
        headers = [t("form.colItem", self.lang), t("form.colUnit", self.lang), t("form.colQty", self.lang),
                   t("form.colPrice", self.lang), t("form.colTotal", self.lang), t("form.colDiscPct", self.lang),
                   t("form.colTax", self.lang), t("form.colNet", self.lang), ""]
        for lbl, text in zip(self.item_header_labels, headers):
            lbl.configure(text=text)

        self.add_item_btn.configure(text=t("form.addItem", self.lang))

        # Totals labels
        self.lbl_subtotal.configure(text=t("form.subtotal", self.lang))
        self.lbl_discount.configure(text=t("form.discountPct", self.lang))
        self.lbl_discount_arrow.configure(text=t("form.discountArrow", self.lang))
        self.lbl_taxable.configure(text=t("form.taxable", self.lang))
        self.lbl_tax.configure(text=t("form.vat15", self.lang))
        self.lbl_net_total.configure(text=t("form.netTotal", self.lang))

        # Payment
        self.lbl_payment.configure(text=t("form.payment", self.lang))
        payment_texts = [translate_payment_type("نقدا", self.lang), translate_payment_type("آجل", self.lang),
                        translate_payment_type("تحويل بنكي", self.lang)]
        for rb, txt in zip(self.payment_radios, payment_texts):
            rb.configure(text=txt)

        # Buttons
        self.btn_cancel.configure(text=t("form.btnClear", self.lang))
        self.btn_save_print.configure(text=t("form.btnSavePrint", self.lang))
        self.btn_save.configure(text=t("form.btnSave", self.lang))

        # Update unit dropdowns in item rows
        for row in self.item_rows:
            if hasattr(row, 'apply_language'):
                row.apply_language(self.lang)

        # Repack for direction
        ps, pso = pack_side(self.lang), pack_side_opposite(self.lang)
        gcl, gcv = grid_column_label(self.lang), grid_column_value(self.lang)
        stk = sticky_for(self.lang)
        jf = justify_for(self.lang)

        for w in [self.lbl_customer_tax, self.customer_tax, self.spacer1, self.lbl_customer_name, self.customer_name]:
            w.pack_forget()
        self.lbl_customer_tax.pack(side=ps, padx=5)
        self.customer_tax.pack(side=ps, padx=5)
        self.spacer1.pack(side=ps)
        self.lbl_customer_name.pack(side=ps, padx=5)
        self.customer_name.pack(side=ps, padx=5)
        for w in [self.lbl_customer_address, self.customer_address, self.spacer2, self.lbl_customer_phone, self.customer_phone]:
            w.pack_forget()
        self.lbl_customer_address.pack(side=ps, padx=5)
        self.customer_address.pack(side=ps, padx=5)
        self.spacer2.pack(side=ps)
        self.lbl_customer_phone.pack(side=ps, padx=5)
        self.customer_phone.pack(side=ps, padx=5)

        for lbl in self.item_header_labels:
            lbl.pack_forget()
        for lbl in self.item_header_labels:
            lbl.pack(side=ps, padx=2)
        self.add_item_btn.pack_forget()
        self.add_item_btn.pack(anchor=pack_anchor_for(self.lang), pady=5)

        self.totals_grid.pack_forget()
        self.totals_grid.pack(anchor=pack_anchor_for(self.lang))
        for lbl in [self.lbl_subtotal, self.lbl_discount, self.lbl_taxable, self.lbl_tax, self.lbl_net_total]:
            lbl.grid_forget()
        for e in [self.subtotal_entry, self.discount_frame, self.taxable_entry, self.tax_entry, self.net_entry]:
            e.grid_forget()
        self.lbl_subtotal.grid(row=0, column=gcl, sticky=stk, padx=5, pady=2)
        self.subtotal_entry.configure(justify=jf)
        self.subtotal_entry.grid(row=0, column=gcv, padx=5, pady=2)
        self.lbl_discount.grid(row=1, column=gcl, sticky=stk, padx=5, pady=2)
        self.discount_frame.grid(row=1, column=gcv, padx=5, pady=2)
        for w in [self.discount_amount_entry, self.lbl_discount_arrow, self.global_discount]:
            w.pack_forget()
        self.discount_amount_entry.configure(justify=jf)
        self.discount_amount_entry.pack(side=pso)
        self.lbl_discount_arrow.pack(side=pso)
        self.global_discount.pack(side=pso)
        self.lbl_taxable.grid(row=3, column=gcl, sticky=stk, padx=5, pady=2)
        self.taxable_entry.configure(justify=jf)
        self.taxable_entry.grid(row=3, column=gcv, padx=5, pady=2)
        self.lbl_tax.grid(row=4, column=gcl, sticky=stk, padx=5, pady=2)
        self.tax_entry.configure(justify=jf)
        self.tax_entry.grid(row=4, column=gcv, padx=5, pady=2)
        self.lbl_net_total.grid(row=5, column=gcl, sticky=stk, padx=5, pady=5)
        self.net_entry.configure(justify=jf)
        self.net_entry.grid(row=5, column=gcv, padx=5, pady=5)

        for rb in self.payment_radios:
            rb.pack_forget()
        self.lbl_payment.pack_forget()
        self.lbl_payment.pack(side=ps, padx=5)
        for rb in self.payment_radios:
            rb.pack(side=ps, padx=10)

        for btn in [self.btn_cancel, self.btn_save_print, self.btn_save]:
            btn.pack_forget()
        self.btn_cancel.pack(side=ps, padx=5)
        self.btn_save_print.pack(side=ps, padx=5)
        self.btn_save.pack(side=ps, padx=5)

        self.form_scrollbar.pack_forget()
        self.main_canvas.pack_forget()
        self.form_scrollbar.pack(side=pso, fill='y')
        self.main_canvas.pack(side=ps, fill='both', expand=True)

        apply_direction_recursive(self, self.lang)
    
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
        self.item_rows[0].unit_var.set(get_unit_display_values(self.lang)[0])
        
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
        self.payment_var.set(payment_type_to_storage(invoice.get('payment_type', 'نقدا')))
        
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
