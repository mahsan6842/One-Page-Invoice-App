"""
Invoice Application - Main Window
Primary application window with navigation tabs
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_database
from ui.invoice_form import InvoiceForm
from ui.invoice_history import InvoiceHistory
from ui.invoice_view import InvoiceView
from ui.settings import SettingsScreen
from ui.widgets import StatusBar


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("نظام الفواتير - Invoice System")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Initialize database
        self.db = get_database()
        
        # Configure styles
        self._configure_styles()
        
        # Create UI
        self._create_menu()
        self._create_toolbar()
        self._create_notebook()
        self._create_statusbar()
        
        # Center window
        self._center_window()
        
        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _configure_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        
        # Use clam theme for better customization
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Configure fonts
        default_font = ('Arial', 10)
        style.configure('.', font=default_font)
        style.configure('TButton', padding=5)
        style.configure('TNotebook.Tab', padding=[15, 5], font=('Arial', 11))
        style.configure('Treeview', rowheight=28)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ملف", menu=file_menu)
        file_menu.add_command(label="فاتورة جديدة", command=self._new_invoice,
                             accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="نسخ احتياطي", command=self._backup)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self._on_close,
                             accelerator="Alt+F4")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="عرض", menu=view_menu)
        view_menu.add_command(label="الرئيسية", command=lambda: self._switch_tab(0))
        view_menu.add_command(label="سجل الفواتير", command=lambda: self._switch_tab(1))
        view_menu.add_command(label="الإعدادات", command=lambda: self._switch_tab(2))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="مساعدة", menu=help_menu)
        help_menu.add_command(label="حول البرنامج", command=self._show_about)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self._new_invoice())
    
    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # Toolbar buttons
        ttk.Button(toolbar, text="🏠 الرئيسية", 
                  command=lambda: self._switch_tab(0), width=12).pack(side='right', padx=2)
        ttk.Button(toolbar, text="📋 السجل", 
                  command=lambda: self._switch_tab(1), width=12).pack(side='right', padx=2)
        ttk.Button(toolbar, text="⚙️ الإعدادات", 
                  command=lambda: self._switch_tab(2), width=12).pack(side='right', padx=2)
        
        # Separator
        ttk.Separator(toolbar, orient='vertical').pack(side='right', fill='y', padx=10)
        
        ttk.Button(toolbar, text="➕ فاتورة جديدة", 
                  command=self._new_invoice, width=15).pack(side='right', padx=2)
        
        # Company name on left
        settings = self.db.get_company_settings()
        company_name = settings.get('company_name_ar', 'نظام الفواتير')
        ttk.Label(toolbar, text=company_name, 
                 font=('Arial', 12, 'bold')).pack(side='left', padx=10)
    
    def _create_notebook(self):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab 1: Create Invoice
        self.invoice_form = InvoiceForm(
            self.notebook,
            on_save=self._on_invoice_saved,
            on_save_print=self._on_invoice_save_print
        )
        self.notebook.add(self.invoice_form, text="   🏠 الرئيسية   ")
        
        # Tab 2: Invoice History
        self.invoice_history = InvoiceHistory(
            self.notebook,
            on_view=self._on_view_invoice,
            on_edit=self._on_edit_invoice
        )
        self.notebook.add(self.invoice_history, text="   📋 سجل الفواتير   ")
        
        # Tab 3: Settings
        self.settings_screen = SettingsScreen(self.notebook)
        self.notebook.add(self.settings_screen, text="   ⚙️ الإعدادات   ")
    
    def _create_statusbar(self):
        """Create status bar"""
        self.statusbar = StatusBar(self.root)
        self.statusbar.pack(fill='x', side='bottom')
        self.statusbar.set_status("جاهز")
    
    def _center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _switch_tab(self, index: int):
        """Switch to specific tab"""
        self.notebook.select(index)
        if index == 1:
            self.invoice_history.refresh()
    
    def _new_invoice(self):
        """Create new invoice"""
        self._switch_tab(0)
        self.invoice_form._clear_form()
    
    def _on_invoice_saved(self, invoice):
        """Handle invoice saved"""
        self.statusbar.set_success(f"تم حفظ الفاتورة رقم {invoice['invoice_number']}")
        self.invoice_history.refresh()
    
    def _on_invoice_save_print(self, invoice):
        """Handle save and print"""
        self.statusbar.set_success(f"تم حفظ الفاتورة رقم {invoice['invoice_number']}")
        self.invoice_history.refresh()
        self._on_view_invoice(invoice, print_mode=True)
    
    def _on_view_invoice(self, invoice, print_mode: bool = False):
        """View invoice"""
        InvoiceView(self.root, invoice, print_mode=print_mode)
    
    def _on_edit_invoice(self, invoice):
        """Edit invoice"""
        self.invoice_form.load_invoice(invoice)
        self._switch_tab(0)
    
    def _backup(self):
        """Create backup from menu"""
        self._switch_tab(2)
        self.settings_screen._create_backup()
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "حول البرنامج",
            "نظام الفواتير\n"
            "Invoice System\n\n"
            "إصدار 1.0.0\n"
            "Version 1.0.0\n\n"
            "نظام لإدارة وطباعة الفواتير\n"
            "مع دعم ضريبة القيمة المضافة"
        )
    
    def _on_close(self):
        """Handle window close"""
        if messagebox.askyesno("تأكيد الخروج", "هل أنت متأكد من الخروج؟"):
            self.db.close()
            self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Application entry point"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
