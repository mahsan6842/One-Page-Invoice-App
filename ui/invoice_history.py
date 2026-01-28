"""
Invoice Application - Invoice History Screen (Enhanced)
List, search, select, and export past invoices
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any, List, Set
from datetime import datetime, timedelta

from app.database import get_database
from ui.widgets import ArabicEntry
from ui.export_dialog import show_export_dialog, ExportProgressDialog


class InvoiceHistory(ttk.Frame):
    """Invoice history list with search, multi-selection, and export functionality"""
    
    def __init__(self, parent, on_view: Callable = None, 
                 on_edit: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_view_callback = on_view
        self.on_edit_callback = on_edit
        self.db = get_database()
        self.current_page = 1
        self.per_page = 50
        
        # Track selected invoice IDs
        self.selected_ids: Set[int] = set()
        self.all_visible_ids: List[int] = []
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self):
        # === Search Bar ===
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        # Search entry
        ttk.Label(search_frame, text="🔍 بحث:").pack(side='right', padx=5)
        self.search_entry = ArabicEntry(search_frame, width=25)
        self.search_entry.pack(side='right', padx=5)
        self.search_entry.bind('<KeyRelease>', self._on_search)
        
        # Date filters
        ttk.Label(search_frame, text="من:").pack(side='right', padx=(20, 5))
        self.date_from = ttk.Entry(search_frame, width=12)
        self.date_from.pack(side='right', padx=5)
        self.date_from.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        
        ttk.Label(search_frame, text="إلى:").pack(side='right', padx=5)
        self.date_to = ttk.Entry(search_frame, width=12)
        self.date_to.pack(side='right', padx=5)
        self.date_to.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Search button
        ttk.Button(search_frame, text="بحث", command=self.refresh).pack(side='right', padx=10)
        
        # === Invoice Table with Checkboxes ===
        table_frame = ttk.Frame(self)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create Treeview with checkbox column
        columns = ('select', 'row_num', 'invoice_number', 'invoice_date', 
                   'customer_name', 'net_total', 'status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                 selectmode='extended', height=18)
        
        # Column configurations
        col_config = [
            ('select', '☐', 40),
            ('row_num', '#', 40),
            ('invoice_number', 'رقم الفاتورة', 120),
            ('invoice_date', 'التاريخ', 100),
            ('customer_name', 'العميل', 180),
            ('net_total', 'الإجمالي', 100),
            ('status', 'الحالة', 70)
        ]
        
        for col_id, header, width in col_config:
            self.tree.heading(col_id, text=header, anchor='center',
                            command=lambda c=col_id: self._on_header_click(c))
            self.tree.column(col_id, width=width, anchor='center', minwidth=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='right', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        # Bindings
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-1>', self._on_click)
        self.tree.bind('<space>', self._toggle_selected)
        
        # === Selection Controls ===
        select_frame = ttk.Frame(self)
        select_frame.pack(fill='x', padx=10, pady=5)
        
        # Select all checkbox
        self.select_all_var = tk.BooleanVar(value=False)
        self.select_all_cb = ttk.Checkbutton(
            select_frame, 
            text="تحديد الكل",
            variable=self.select_all_var,
            command=self._on_select_all
        )
        self.select_all_cb.pack(side='right', padx=5)
        
        # Selection count label
        self.selection_label = ttk.Label(select_frame, text="(0 محدد)")
        self.selection_label.pack(side='right', padx=10)
        
        # Clear selection button
        ttk.Button(select_frame, text="إلغاء التحديد", 
                  command=self._clear_selection, width=12).pack(side='right', padx=5)
        
        # === Export Buttons ===
        export_frame = ttk.LabelFrame(self, text="تصدير", padding=5)
        export_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(export_frame, text="📊 تصدير CSV / Excel", 
                  command=self._export_csv, width=18).pack(side='right', padx=5)
        ttk.Button(export_frame, text="📄 تصدير PDF", 
                  command=self._export_pdf, width=18).pack(side='right', padx=5)
        
        # Export info label
        self.export_info = ttk.Label(export_frame, text="حدد الفواتير للتصدير", foreground='gray')
        self.export_info.pack(side='right', padx=20)
        
        # === Action Buttons ===
        action_frame = ttk.Frame(self)
        action_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(action_frame, text="👁️ عرض", command=self._view_selected,
                  width=10).pack(side='right', padx=3)
        ttk.Button(action_frame, text="🖨️ طباعة", command=self._print_selected,
                  width=10).pack(side='right', padx=3)
        ttk.Button(action_frame, text="❌ إلغاء", command=self._cancel_selected,
                  width=10).pack(side='right', padx=3)
        ttk.Button(action_frame, text="🔄 تحديث", command=self.refresh,
                  width=10).pack(side='right', padx=3)
        
        # === Summary Bar ===
        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        self.count_label = ttk.Label(summary_frame, text="إجمالي الفواتير: 0")
        self.count_label.pack(side='right', padx=20)
        
        self.total_label = ttk.Label(summary_frame, text="إجمالي المبيعات: 0.00 ريال")
        self.total_label.pack(side='right', padx=20)
        
        # Pagination
        self.page_label = ttk.Label(summary_frame, text="صفحة 1")
        self.page_label.pack(side='left', padx=5)
        
        ttk.Button(summary_frame, text="◀", command=self._next_page,
                  width=3).pack(side='left', padx=2)
        ttk.Button(summary_frame, text="▶", command=self._prev_page,
                  width=3).pack(side='left', padx=2)
    
    def refresh(self):
        """Refresh invoice list"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.all_visible_ids = []
        
        # Get filter values
        search_term = self.search_entry.get().strip()
        start_date = self.date_from.get().strip() or None
        end_date = self.date_to.get().strip() or None
        
        # Fetch invoices
        invoices = self.db.get_invoices(
            page=self.current_page,
            per_page=self.per_page,
            start_date=start_date,
            end_date=end_date,
            search_term=search_term if search_term else None
        )
        
        # Insert into tree
        for i, inv in enumerate(invoices, 1):
            inv_id = inv['id']
            self.all_visible_ids.append(inv_id)
            
            # Check if selected
            is_selected = inv_id in self.selected_ids
            select_mark = '☑' if is_selected else '☐'
            
            status_text = 'نشطة' if inv['status'] == 'active' else 'ملغاة'
            
            self.tree.insert('', tk.END, values=(
                select_mark,
                i + (self.current_page - 1) * self.per_page,
                inv['invoice_number'],
                inv['invoice_date'],
                inv['customer_name'] or '-',
                f"{inv['net_total']:,.2f}",
                status_text
            ), tags=(str(inv_id),))
        
        # Update summary
        count = self.db.get_invoices_count(start_date, end_date, 
                                           search_term if search_term else None)
        total = self.db.get_invoices_total(start_date, end_date)
        
        self.count_label.configure(text=f"إجمالي الفواتير: {count}")
        self.total_label.configure(text=f"إجمالي المبيعات: {total:,.2f} ريال")
        self.page_label.configure(text=f"صفحة {self.current_page}")
        
        self._update_selection_display()
    
    def _on_header_click(self, column: str):
        """Handle header click - toggle all if clicking checkbox column"""
        if column == 'select':
            self._on_select_all()
    
    def _on_click(self, event):
        """Handle click on row"""
        # Get clicked item
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if item and column == '#1':  # Checkbox column
            self._toggle_item(item)
            return 'break'  # Prevent default selection
    
    def _toggle_item(self, item: str):
        """Toggle selection for an item"""
        tags = self.tree.item(item)['tags']
        if tags:
            inv_id = int(tags[0])
            
            if inv_id in self.selected_ids:
                self.selected_ids.remove(inv_id)
                new_mark = '☐'
            else:
                self.selected_ids.add(inv_id)
                new_mark = '☑'
            
            # Update display
            values = list(self.tree.item(item)['values'])
            values[0] = new_mark
            self.tree.item(item, values=values)
            
            self._update_selection_display()
    
    def _toggle_selected(self, event=None):
        """Toggle selection for currently highlighted rows"""
        for item in self.tree.selection():
            self._toggle_item(item)
    
    def _on_select_all(self):
        """Select or deselect all visible invoices"""
        select_all = self.select_all_var.get()
        
        if select_all:
            # Add all visible to selection
            self.selected_ids.update(self.all_visible_ids)
        else:
            # Remove all visible from selection
            self.selected_ids -= set(self.all_visible_ids)
        
        # Update display
        for item in self.tree.get_children():
            tags = self.tree.item(item)['tags']
            if tags:
                inv_id = int(tags[0])
                is_selected = inv_id in self.selected_ids
                values = list(self.tree.item(item)['values'])
                values[0] = '☑' if is_selected else '☐'
                self.tree.item(item, values=values)
        
        self._update_selection_display()
    
    def _clear_selection(self):
        """Clear all selections"""
        self.selected_ids.clear()
        self.select_all_var.set(False)
        self.refresh()
    
    def _update_selection_display(self):
        """Update selection count display"""
        count = len(self.selected_ids)
        self.selection_label.configure(text=f"({count} محدد)")
        
        if count > 0:
            self.export_info.configure(text=f"جاهز لتصدير {count} فاتورة", foreground='green')
        else:
            self.export_info.configure(text="حدد الفواتير للتصدير", foreground='gray')
        
        # Update select all checkbox state
        all_visible_selected = all(id in self.selected_ids for id in self.all_visible_ids)
        self.select_all_var.set(all_visible_selected and len(self.all_visible_ids) > 0)
    
    def _get_selected_invoice_ids(self) -> List[int]:
        """Get list of selected invoice IDs"""
        return list(self.selected_ids)
    
    def _on_search(self, event=None):
        """Handle search input"""
        if hasattr(self, '_search_after_id'):
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(300, self.refresh)
    
    def _get_clicked_invoice_id(self) -> Optional[int]:
        """Get invoice ID from current tree selection (single)"""
        selection = self.tree.selection()
        if selection:
            tags = self.tree.item(selection[0])['tags']
            if tags:
                return int(tags[0])
        return None
    
    # ==================== Export Functions ====================
    
    def _export_csv(self):
        """Export selected invoices to CSV"""
        invoice_ids = self._get_selected_invoice_ids()
        
        if not invoice_ids:
            messagebox.showwarning("تنبيه", "يرجى تحديد فاتورة واحدة على الأقل للتصدير")
            return
        
        # Show export dialog
        show_export_dialog(
            self.winfo_toplevel(),
            'csv',
            invoice_ids,
            on_complete=self._on_export_complete
        )
    
    def _export_pdf(self):
        """Export selected invoices to PDF"""
        invoice_ids = self._get_selected_invoice_ids()
        
        if not invoice_ids:
            messagebox.showwarning("تنبيه", "يرجى تحديد فاتورة واحدة على الأقل للتصدير")
            return
        
        # Show export dialog
        show_export_dialog(
            self.winfo_toplevel(),
            'pdf',
            invoice_ids,
            on_complete=self._on_export_complete
        )
    
    def _on_export_complete(self, success: bool, count: int):
        """Handle export completion"""
        if success:
            # Optionally clear selection after successful export
            pass
    
    # ==================== Action Functions ====================
    
    def _view_selected(self):
        """View selected invoice"""
        invoice_id = self._get_clicked_invoice_id()
        if invoice_id:
            invoice = self.db.get_invoice(invoice_id)
            if invoice and self.on_view_callback:
                self.on_view_callback(invoice)
        else:
            messagebox.showwarning("تنبيه", "يرجى اختيار فاتورة للعرض")
    
    def _print_selected(self):
        """Print selected invoice"""
        invoice_id = self._get_clicked_invoice_id()
        if invoice_id:
            invoice = self.db.get_invoice(invoice_id)
            if invoice and self.on_view_callback:
                self.on_view_callback(invoice, print_mode=True)
        else:
            messagebox.showwarning("تنبيه", "يرجى اختيار فاتورة للطباعة")
    
    def _cancel_selected(self):
        """Cancel selected invoice"""
        invoice_id = self._get_clicked_invoice_id()
        if invoice_id:
            if messagebox.askyesno("تأكيد", "هل أنت متأكد من إلغاء هذه الفاتورة؟"):
                self.db.cancel_invoice(invoice_id)
                self.refresh()
                messagebox.showinfo("نجاح", "تم إلغاء الفاتورة")
        else:
            messagebox.showwarning("تنبيه", "يرجى اختيار فاتورة")
    
    def _on_double_click(self, event):
        """Handle double-click on row"""
        # Check if clicking on checkbox column
        column = self.tree.identify_column(event.x)
        if column == '#1':
            return
        self._view_selected()
    
    def _prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh()
    
    def _next_page(self):
        """Go to next page"""
        self.current_page += 1
        self.refresh()
