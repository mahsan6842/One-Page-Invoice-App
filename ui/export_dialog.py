"""
Invoice Application - Export Dialog
Progress dialog for export operations with background processing
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from typing import List, Callable, Optional

from app.exporter import get_exporter
from app.i18n import LANG_EN, get_current_lang


class ExportProgressDialog(tk.Toplevel):
    """
    Progress dialog for export operations.
    Runs export in background thread to prevent UI freezing.
    """
    
    def __init__(self, parent, export_type: str, invoice_ids: List[int],
                 output_path: str, on_complete: Callable = None):
        """
        Initialize export progress dialog.
        
        Args:
            parent: Parent window
            export_type: 'csv' or 'pdf'
            invoice_ids: List of invoice IDs to export
            output_path: Output file path (CSV) or folder path (PDF)
            on_complete: Callback when export completes
        """
        super().__init__(parent)
        
        self.export_type = export_type
        self.invoice_ids = invoice_ids
        self.output_path = output_path
        self.on_complete = on_complete
        self.exporter = get_exporter()
        self.lang = get_current_lang()
        self.export_thread = None
        self.is_cancelled = False
        
        # Result storage
        self.result_success = False
        self.result_message = ""
        self.result_count = 0
        self.result_errors = []
        
        self._setup_window()
        self._create_widgets()
        self._start_export()
    
    def _setup_window(self):
        """Configure window properties"""
        title = ("Export CSV" if self.export_type == 'csv' else "Export PDF") if self.lang == LANG_EN else ("تصدير CSV" if self.export_type == 'csv' else "تصدير PDF")
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Make modal
        self.transient(self.master)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 400) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title label
        self.title_label = ttk.Label(
            main_frame, 
            text="Exporting..." if self.lang == LANG_EN else "جاري التصدير...",
            font=('Arial', 12, 'bold')
        )
        self.title_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=350,
            mode='determinate'
        )
        self.progress_bar.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Preparing..." if self.lang == LANG_EN else "جاري التحضير...",
            font=('Arial', 10)
        )
        self.status_label.pack(pady=5)
        
        # Progress count label
        self.count_label = ttk.Label(
            main_frame,
            text="0 / 0",
            font=('Arial', 9)
        )
        self.count_label.pack(pady=5)
        
        # Cancel button
        self.cancel_btn = ttk.Button(
            main_frame,
            text="Cancel" if self.lang == LANG_EN else "إلغاء",
            command=self._on_cancel,
            width=15
        )
        self.cancel_btn.pack(pady=15)
    
    def _start_export(self):
        """Start export in background thread"""
        self.export_thread = threading.Thread(target=self._run_export, daemon=True)
        self.export_thread.start()
        
        # Start checking for completion
        self._check_completion()
    
    def _run_export(self):
        """Run export operation (called in background thread)"""
        try:
            if self.export_type == 'csv':
                success, message = self.exporter.export_to_csv(
                    self.invoice_ids,
                    self.output_path,
                    progress_callback=self._update_progress,
                    lang=self.lang,
                )
                self.result_success = success
                self.result_message = message
                self.result_count = len(self.invoice_ids) if success else 0
                
            else:  # PDF
                success_count, total, errors = self.exporter.export_to_pdf(
                    self.invoice_ids,
                    self.output_path,
                    progress_callback=self._update_progress,
                    lang=self.lang,
                )
                self.result_success = success_count > 0
                self.result_count = success_count
                self.result_errors = errors
                
                if success_count == total:
                    self.result_message = f"Exported {success_count} invoice(s) successfully." if self.lang == LANG_EN else f"تم تصدير {success_count} فاتورة بنجاح"
                elif success_count > 0:
                    self.result_message = f"Exported {success_count} of {total} invoice(s)." if self.lang == LANG_EN else f"تم تصدير {success_count} من {total} فاتورة"
                else:
                    self.result_message = "Export failed." if self.lang == LANG_EN else "فشل التصدير"
                    
        except Exception as e:
            self.result_success = False
            self.result_message = f"Error: {str(e)}" if self.lang == LANG_EN else f"حدث خطأ: {str(e)}"
    
    def _update_progress(self, current: int, total: int, message: str):
        """
        Update progress (called from background thread).
        Uses after() to safely update UI from main thread.
        """
        if self.is_cancelled:
            return
        
        # Calculate percentage
        percentage = (current / total * 100) if total > 0 else 0
        
        # Schedule UI update on main thread
        self.after(0, self._set_progress, percentage, current, total, message)
    
    def _set_progress(self, percentage: float, current: int, total: int, message: str):
        """Set progress values (called on main thread)"""
        if self.is_cancelled:
            return
        
        self.progress_var.set(percentage)
        self.status_label.configure(text=message)
        self.count_label.configure(text=f"{current} / {total}")
    
    def _check_completion(self):
        """Check if export thread has completed"""
        if self.export_thread and self.export_thread.is_alive():
            # Still running, check again later
            self.after(100, self._check_completion)
        else:
            # Export completed
            self._on_export_complete()
    
    def _on_export_complete(self):
        """Handle export completion"""
        if self.is_cancelled:
            return
        
        # Update progress to 100%
        self.progress_var.set(100)
        self.status_label.configure(text="Done!" if self.lang == LANG_EN else "اكتمل!")
        
        # Close dialog after short delay
        self.after(500, self._show_result)
    
    def _show_result(self):
        """Show export result and close dialog"""
        self.destroy()
        
        if self.result_success:
            # Success dialog with option to open folder
            self._show_success_dialog()
        else:
            # Error dialog
            title = "Export error" if self.lang == LANG_EN else "خطأ في التصدير"
            messagebox.showerror(title, self.result_message)
        
        # Call completion callback
        if self.on_complete:
            self.on_complete(self.result_success, self.result_count)
    
    def _show_success_dialog(self):
        """Show success dialog with open folder option"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Export complete" if self.lang == LANG_EN else "اكتمل التصدير")
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Center on parent
        dialog.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 350) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 180) // 2
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Success icon and message
        ttk.Label(frame, text="✓", font=('Arial', 24), foreground='green').pack()
        ttk.Label(frame, text=self.result_message, font=('Arial', 11)).pack(pady=10)
        
        # Show path
        if self.export_type == 'csv':
            path_text = os.path.basename(self.output_path)
        else:
            path_text = self.output_path
        ttk.Label(frame, text=path_text, font=('Arial', 9), foreground='gray').pack()
        
        # Show errors if any
        if self.result_errors:
            error_text = f"({len(self.result_errors)} errors)" if self.lang == LANG_EN else f"({len(self.result_errors)} أخطاء)"
            ttk.Label(frame, text=error_text, foreground='orange').pack()
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)
        
        def open_folder():
            folder = self.output_path if self.export_type == 'pdf' else os.path.dirname(self.output_path)
            if os.path.exists(folder):
                os.startfile(folder)
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Open folder" if self.lang == LANG_EN else "فتح المجلد", command=open_folder,
                  width=12).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Close" if self.lang == LANG_EN else "إغلاق", command=dialog.destroy,
                  width=12).pack(side='right', padx=5)
    
    def _on_cancel(self):
        """Handle cancel button or window close"""
        self.is_cancelled = True
        self.exporter.cancel()
        self.status_label.configure(text="Cancelling..." if self.lang == LANG_EN else "جاري الإلغاء...")
        self.cancel_btn.configure(state='disabled')
        
        # Wait briefly for thread to finish, then close
        self.after(500, self.destroy)


class ExportOptionsDialog(tk.Toplevel):
    """
    Dialog to choose export options before starting export.
    """
    
    def __init__(self, parent, invoice_count: int, on_export: Callable):
        """
        Initialize export options dialog.
        
        Args:
            parent: Parent window
            invoice_count: Number of selected invoices
            on_export: Callback(export_type, output_path) when user confirms
        """
        super().__init__(parent)
        
        self.invoice_count = invoice_count
        self.on_export = on_export
        self.exporter = get_exporter()
        self.lang = get_current_lang()
        
        self._setup_window()
        self._create_widgets()
    
    def _setup_window(self):
        """Configure window"""
        self.title("Export options" if self.lang == LANG_EN else "خيارات التصدير")
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()
        
        # Center
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 400) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 300) // 2
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Header
        header = f"Export {self.invoice_count} invoice(s)" if self.lang == LANG_EN else f"تصدير {self.invoice_count} فاتورة"
        ttk.Label(frame, text=header, font=('Arial', 12, 'bold')).pack(anchor='e', pady=(0, 15))
        
        # Export type selection
        type_frame = ttk.LabelFrame(frame, text="Export type" if self.lang == LANG_EN else "نوع التصدير", padding=10)
        type_frame.pack(fill='x', pady=10)
        
        self.export_type = tk.StringVar(value='csv')
        
        csv_frame = ttk.Frame(type_frame)
        csv_frame.pack(fill='x', pady=5)
        ttk.Radiobutton(csv_frame, text="CSV / Excel", variable=self.export_type,
                       value='csv', command=self._on_type_change).pack(side='right')
        csv_time = self.exporter.estimate_export_time(self.invoice_count, 'csv')
        csv_hint = f"(single file - {csv_time})" if self.lang == LANG_EN else f"(ملف واحد - {csv_time})"
        ttk.Label(csv_frame, text=csv_hint,
                 foreground='gray').pack(side='right', padx=10)
        
        pdf_frame = ttk.Frame(type_frame)
        pdf_frame.pack(fill='x', pady=5)
        ttk.Radiobutton(pdf_frame, text="PDF", variable=self.export_type,
                       value='pdf', command=self._on_type_change).pack(side='right')
        pdf_time = self.exporter.estimate_export_time(self.invoice_count, 'pdf')
        pdf_hint = f"(separate files - {pdf_time})" if self.lang == LANG_EN else f"(ملفات منفصلة - {pdf_time})"
        ttk.Label(pdf_frame, text=pdf_hint,
                 foreground='gray').pack(side='right', padx=10)
        
        # Description
        self.desc_label = ttk.Label(frame, text="", wraplength=350, justify='right')
        self.desc_label.pack(fill='x', pady=10)
        self._update_description()
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=20)
        
        ttk.Button(btn_frame, text="Cancel" if self.lang == LANG_EN else "إلغاء", command=self.destroy,
                  width=12).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export" if self.lang == LANG_EN else "تصدير", command=self._on_export,
                  width=12).pack(side='right', padx=5)
    
    def _on_type_change(self):
        """Handle export type change"""
        self._update_description()
    
    def _update_description(self):
        """Update description based on selected type"""
        if self.export_type.get() == 'csv':
            desc = "All selected invoices will be exported to a single CSV file (Excel-friendly)." if self.lang == LANG_EN else "سيتم تصدير جميع الفواتير المحددة في ملف CSV واحد يمكن فتحه في Excel."
        else:
            desc = "A separate PDF will be generated for each invoice in the selected folder." if self.lang == LANG_EN else "سيتم إنشاء ملف PDF منفصل لكل فاتورة في المجلد المحدد."
        self.desc_label.configure(text=desc)
    
    def _on_export(self):
        """Handle export button click"""
        export_type = self.export_type.get()
        
        if export_type == 'csv':
            # Ask for file path
            default_name = self.exporter.get_default_csv_filename()
            filepath = filedialog.asksaveasfilename(
                parent=self,
                title="Save CSV" if self.lang == LANG_EN else "حفظ ملف CSV",
                defaultextension='.csv',
                filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
                initialfile=default_name
            )
            
            if filepath:
                self.destroy()
                self.on_export('csv', filepath)
        else:
            # Ask for folder
            default_folder = self.exporter.get_default_pdf_folder()
            folder = filedialog.askdirectory(
                parent=self,
                title="Choose PDF output folder" if self.lang == LANG_EN else "اختر مجلد حفظ ملفات PDF",
                initialdir=default_folder
            )
            
            if folder:
                self.destroy()
                self.on_export('pdf', folder)


def show_export_dialog(parent, export_type: str, invoice_ids: List[int],
                       on_complete: Callable = None):
    """
    Show export dialog and handle file/folder selection.
    
    Args:
        parent: Parent window
        export_type: 'csv' or 'pdf'
        invoice_ids: List of invoice IDs to export
        on_complete: Callback when export completes
    """
    exporter = get_exporter()
    lang = get_current_lang()
    
    if export_type == 'csv':
        # Ask for CSV file path
        default_name = exporter.get_default_csv_filename()
        filepath = filedialog.asksaveasfilename(
            parent=parent,
            title="Save CSV" if lang == LANG_EN else "حفظ ملف CSV",
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            initialfile=default_name
        )
        
        if filepath:
            ExportProgressDialog(parent, 'csv', invoice_ids, filepath, on_complete)
    
    else:  # PDF
        # Ask for folder
        default_folder = exporter.get_default_pdf_folder()
        folder = filedialog.askdirectory(
            parent=parent,
            title="Choose PDF output folder" if lang == LANG_EN else "اختر مجلد حفظ ملفات PDF",
            initialdir=default_folder
        )
        
        if folder:
            ExportProgressDialog(parent, 'pdf', invoice_ids, folder, on_complete)
