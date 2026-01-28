"""
Invoice Application - Invoice History Screen (Enhanced)
List, search, select, and export past invoices
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any, List, Set
from datetime import datetime, timedelta

from app.database import get_database
from app.i18n import LANG_AR, LANG_EN, t
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
        self.lang = LANG_AR
        
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
        self.search_label = ttk.Label(search_frame, text=t("history.searchLabel", self.lang))
        self.search_label.pack(side='right', padx=5)
        self.search_entry = ArabicEntry(search_frame, width=25)
        self.search_entry.pack(side='right', padx=5)
        self.search_entry.bind('<KeyRelease>', self._on_search)
        
        # Date filters
        self.from_label = ttk.Label(search_frame, text=t("common.from", self.lang))
        self.from_label.pack(side='right', padx=(20, 5))
        self.date_from = ttk.Entry(search_frame, width=12)
        self.date_from.pack(side='right', padx=5)
        self.date_from.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        
        self.to_label = ttk.Label(search_frame, text=t("common.to", self.lang))
        self.to_label.pack(side='right', padx=5)
        self.date_to = ttk.Entry(search_frame, width=12)
        self.date_to.pack(side='right', padx=5)
        self.date_to.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Search button
        self.search_btn = ttk.Button(search_frame, text=t("common.search", self.lang), command=self.refresh)
        self.search_btn.pack(side='right', padx=10)
        
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
            ('select', t("history.col.select", self.lang), 40),
            ('row_num', t("history.col.row", self.lang), 40),
            ('invoice_number', t("history.col.number", self.lang), 120),
            ('invoice_date', t("history.col.date", self.lang), 100),
            ('customer_name', t("history.col.customer", self.lang), 180),
            ('net_total', t("history.col.total", self.lang), 100),
            ('status', t("history.col.status", self.lang), 70)
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
            text=t("history.selectAll", self.lang),
            variable=self.select_all_var,
            command=self._on_select_all
        )
        self.select_all_cb.pack(side='right', padx=5)
        
        # Selection count label
        self.selection_label = ttk.Label(select_frame, text=t("history.selectedCount", self.lang, count=0))
        self.selection_label.pack(side='right', padx=10)
        
        # Clear selection button
        self.clear_btn = ttk.Button(select_frame, text=t("history.clearSelection", self.lang),
                                    command=self._clear_selection, width=12)
        self.clear_btn.pack(side='right', padx=5)
        
        # === Export Buttons ===
        self.export_frame = ttk.LabelFrame(self, text=t("history.exportGroup", self.lang), padding=5)
        self.export_frame.pack(fill='x', padx=10, pady=5)
        
        self.export_csv_btn = ttk.Button(self.export_frame, text=t("history.exportCsv", self.lang),
                                         command=self._export_csv, width=18)
        self.export_csv_btn.pack(side='right', padx=5)
        self.export_pdf_btn = ttk.Button(self.export_frame, text=t("history.exportPdf", self.lang),
                                         command=self._export_pdf, width=18)
        self.export_pdf_btn.pack(side='right', padx=5)
        
        # Export info label
        self.export_info = ttk.Label(self.export_frame, text=t("history.exportHint", self.lang), foreground='gray')
        self.export_info.pack(side='right', padx=20)
        
        # === Action Buttons ===
        action_frame = ttk.Frame(self)
        action_frame.pack(fill='x', padx=10, pady=5)
        
        self.view_btn = ttk.Button(action_frame, text=t("history.action.view", self.lang),
                                   command=self._view_selected, width=10)
        self.view_btn.pack(side='right', padx=3)
        self.print_btn = ttk.Button(action_frame, text=t("history.action.print", self.lang),
                                    command=self._print_selected, width=10)
        self.print_btn.pack(side='right', padx=3)
        self.cancel_btn = ttk.Button(action_frame, text=t("history.action.cancel", self.lang),
                                     command=self._cancel_selected, width=10)
        self.cancel_btn.pack(side='right', padx=3)
        self.refresh_btn = ttk.Button(action_frame, text=t("history.action.refresh", self.lang),
                                      command=self.refresh, width=10)
        self.refresh_btn.pack(side='right', padx=3)
        
        # === Summary Bar ===
        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        self.count_label = ttk.Label(summary_frame, text=t("history.summary.count", self.lang, count=0))
        self.count_label.pack(side='right', padx=20)
        
        self.total_label = ttk.Label(summary_frame, text=t("history.summary.total", self.lang, total="0.00"))
        self.total_label.pack(side='right', padx=20)
        
        # Pagination
        self.page_label = ttk.Label(summary_frame, text=t("history.page", self.lang, page=1))
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
            
            status_text = t("status.active", self.lang) if inv['status'] == 'active' else t("status.cancelled", self.lang)
            
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
        
        self.count_label.configure(text=t("history.summary.count", self.lang, count=count))
        self.total_label.configure(text=t("history.summary.total", self.lang, total=f"{total:,.2f}"))
        self.page_label.configure(text=t("history.page", self.lang, page=self.current_page))
        
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
        self.selection_label.configure(text=t("history.selectedCount", self.lang, count=count))
        
        if count > 0:
            msg = f"جاهز لتصدير {count} فاتورة" if self.lang != LANG_EN else f"Ready to export {count} invoice(s)"
            self.export_info.configure(text=msg, foreground='green')
        else:
            self.export_info.configure(text=t("history.exportHint", self.lang), foreground='gray')
        
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
            title = "تنبيه" if self.lang != LANG_EN else "Warning"
            msg = "يرجى تحديد فاتورة واحدة على الأقل للتصدير" if self.lang != LANG_EN else "Please select at least one invoice to export."
            messagebox.showwarning(title, msg)
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
            title = "تنبيه" if self.lang != LANG_EN else "Warning"
            msg = "يرجى تحديد فاتورة واحدة على الأقل للتصدير" if self.lang != LANG_EN else "Please select at least one invoice to export."
            messagebox.showwarning(title, msg)
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
            title = "تنبيه" if self.lang != LANG_EN else "Warning"
            msg = "يرجى اختيار فاتورة للعرض" if self.lang != LANG_EN else "Please select an invoice to view."
            messagebox.showwarning(title, msg)
    
    def _print_selected(self):
        """Print selected invoice"""
        invoice_id = self._get_clicked_invoice_id()
        if invoice_id:
            invoice = self.db.get_invoice(invoice_id)
            if invoice and self.on_view_callback:
                self.on_view_callback(invoice, print_mode=True)
        else:
            title = "تنبيه" if self.lang != LANG_EN else "Warning"
            msg = "يرجى اختيار فاتورة للطباعة" if self.lang != LANG_EN else "Please select an invoice to print."
            messagebox.showwarning(title, msg)
    
    def _cancel_selected(self):
        """Cancel selected invoice"""
        invoice_id = self._get_clicked_invoice_id()
        if invoice_id:
            title = t("common.confirm", self.lang)
            msg = "هل أنت متأكد من إلغاء هذه الفاتورة؟" if self.lang != LANG_EN else "Are you sure you want to cancel this invoice?"
            if messagebox.askyesno(title, msg):
                self.db.cancel_invoice(invoice_id)
                self.refresh()
                messagebox.showinfo(t("common.success", self.lang),
                                    "تم إلغاء الفاتورة" if self.lang != LANG_EN else "Invoice cancelled.")
        else:
            title = "تنبيه" if self.lang != LANG_EN else "Warning"
            msg = "يرجى اختيار فاتورة" if self.lang != LANG_EN else "Please select an invoice."
            messagebox.showwarning(title, msg)
    
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

    def apply_language(self, lang: str):
        """Update all visible texts to selected language."""
        self.lang = lang or LANG_AR

        # Search bar labels
        self.search_label.configure(text=t("history.searchLabel", self.lang))
        self.from_label.configure(text=t("common.from", self.lang))
        self.to_label.configure(text=t("common.to", self.lang))
        self.search_btn.configure(text=t("common.search", self.lang))

        # Tree headings
        try:
            self.tree.heading('select', text=t("history.col.select", self.lang), anchor='center')
            self.tree.heading('row_num', text=t("history.col.row", self.lang), anchor='center')
            self.tree.heading('invoice_number', text=t("history.col.number", self.lang), anchor='center')
            self.tree.heading('invoice_date', text=t("history.col.date", self.lang), anchor='center')
            self.tree.heading('customer_name', text=t("history.col.customer", self.lang), anchor='center')
            self.tree.heading('net_total', text=t("history.col.total", self.lang), anchor='center')
            self.tree.heading('status', text=t("history.col.status", self.lang), anchor='center')
        except Exception:
            pass

        # Selection / export controls
        self.select_all_cb.configure(text=t("history.selectAll", self.lang))
        self.clear_btn.configure(text=t("history.clearSelection", self.lang))
        self.export_frame.configure(text=t("history.exportGroup", self.lang))
        self.export_csv_btn.configure(text=t("history.exportCsv", self.lang))
        self.export_pdf_btn.configure(text=t("history.exportPdf", self.lang))

        # Action buttons
        self.view_btn.configure(text=t("history.action.view", self.lang))
        self.print_btn.configure(text=t("history.action.print", self.lang))
        self.cancel_btn.configure(text=t("history.action.cancel", self.lang))
        self.refresh_btn.configure(text=t("history.action.refresh", self.lang))

        # Update dynamic displays
        self._update_selection_display()
        self.refresh()
