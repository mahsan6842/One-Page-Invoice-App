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
from app.i18n import LANG_AR, LANG_EN, t, set_current_lang, pack_side, pack_side_opposite
from ui.invoice_form import InvoiceForm
from ui.invoice_history import InvoiceHistory
from ui.invoice_view import InvoiceView
from ui.settings import SettingsScreen
from ui.widgets import StatusBar


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root._main_window = self  # For dialogs to register for language updates
        self._open_dialogs = []  # Track open Toplevels for language propagation
        # Initialize database
        self.db = get_database()
        settings = self.db.get_company_settings()
        self.lang = settings.get('ui_language', LANG_AR) or LANG_AR
        set_current_lang(self.lang)

        self.root.title(t("app.title", self.lang))
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Configure styles
        self._configure_styles()
        
        # Create UI
        self._create_menu()
        self._create_toolbar()
        self._create_notebook()
        self._create_statusbar()

        # Apply initial language to all UI
        self.apply_language(self.lang)
        
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
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=t("menu.file", self.lang), menu=self.file_menu)
        self.file_menu.add_command(label=t("menu.newInvoice", self.lang), command=self._new_invoice,
                                   accelerator="Ctrl+N")
        self.file_menu.add_separator()
        self.file_menu.add_command(label=t("menu.backup", self.lang), command=self._backup)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=t("menu.exit", self.lang), command=self._on_close,
                                   accelerator="Alt+F4")
        
        # View menu
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=t("menu.view", self.lang), menu=self.view_menu)
        self.view_menu.add_command(label=t("menu.home", self.lang), command=lambda: self._switch_tab(0))
        self.view_menu.add_command(label=t("menu.history", self.lang), command=lambda: self._switch_tab(1))
        self.view_menu.add_command(label=t("menu.settings", self.lang), command=lambda: self._switch_tab(2))

        # Language menu
        self.lang_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=t("menu.language", self.lang), menu=self.lang_menu)
        self.lang_var = tk.StringVar(value=self.lang)
        self.lang_menu.add_radiobutton(
            label=t("menu.language.en", self.lang),
            value=LANG_EN,
            variable=self.lang_var,
            command=self._on_language_change,
        )
        self.lang_menu.add_radiobutton(
            label=t("menu.language.ar", self.lang),
            value=LANG_AR,
            variable=self.lang_var,
            command=self._on_language_change,
        )
        
        # Help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=t("menu.help", self.lang), menu=self.help_menu)
        self.help_menu.add_command(label=t("menu.about", self.lang), command=self._show_about)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self._new_invoice())
    
    def _create_toolbar(self):
        """Create toolbar"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill='x', padx=5, pady=5)
        ps = pack_side(self.lang)
        pso = pack_side_opposite(self.lang)
        self.btn_home = ttk.Button(self.toolbar, text=t("toolbar.home", self.lang),
                                   command=lambda: self._switch_tab(0), width=12)
        self.btn_home.pack(side=ps, padx=2)
        self.btn_history = ttk.Button(self.toolbar, text=t("toolbar.history", self.lang),
                                      command=lambda: self._switch_tab(1), width=12)
        self.btn_history.pack(side=ps, padx=2)
        self.btn_settings = ttk.Button(self.toolbar, text=t("toolbar.settings", self.lang),
                                       command=lambda: self._switch_tab(2), width=12)
        self.btn_settings.pack(side=ps, padx=2)
        self.toolbar_sep = ttk.Separator(self.toolbar, orient='vertical')
        self.toolbar_sep.pack(side=ps, fill='y', padx=10)
        self.btn_new_invoice = ttk.Button(self.toolbar, text=t("toolbar.newInvoice", self.lang),
                                          command=self._new_invoice, width=15)
        self.btn_new_invoice.pack(side=ps, padx=2)
        settings = self.db.get_company_settings()
        self.company_label = ttk.Label(self.toolbar, text=settings.get('company_name_ar', 'نظام الفواتير'),
                                       font=('Arial', 12, 'bold'))
        self.company_label.pack(side=pso, padx=10)
    
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
        self.notebook.add(self.invoice_form, text=t("tab.home", self.lang))
        
        # Tab 2: Invoice History
        self.invoice_history = InvoiceHistory(
            self.notebook,
            on_view=self._on_view_invoice,
            on_edit=self._on_edit_invoice
        )
        self.notebook.add(self.invoice_history, text=t("tab.history", self.lang))
        
        # Tab 3: Settings
        self.settings_screen = SettingsScreen(self.notebook)
        self.notebook.add(self.settings_screen, text=t("tab.settings", self.lang))
    
    def _create_statusbar(self):
        """Create status bar"""
        self.statusbar = StatusBar(self.root)
        self.statusbar.pack(fill='x', side='bottom')
        self.statusbar.set_status(t("common.ready", self.lang))

    def _on_language_change(self):
        """Handle language selection from menu"""
        new_lang = self.lang_var.get() or LANG_AR
        if new_lang == self.lang:
            return
        self.lang = new_lang
        set_current_lang(self.lang)
        try:
            self.db.update_company_settings(ui_language=self.lang)
        except Exception as e:
            print(f"Failed to persist language: {e}")
        self.apply_language(self.lang)

    def apply_language(self, lang: str):
        """Apply language to all UI elements."""
        set_current_lang(lang)
        self.root.title(t("app.title", lang))

        # Update menubar cascade labels
        try:
            self.menubar.entryconfigure(0, label=t("menu.file", lang))
            self.menubar.entryconfigure(1, label=t("menu.view", lang))
            self.menubar.entryconfigure(2, label=t("menu.language", lang))
            self.menubar.entryconfigure(3, label=t("menu.help", lang))
        except Exception:
            pass

        # Re-label menu items (order matters)
        try:
            self.file_menu.entryconfigure(0, label=t("menu.newInvoice", lang))
            self.file_menu.entryconfigure(2, label=t("menu.backup", lang))
            self.file_menu.entryconfigure(4, label=t("menu.exit", lang))
        except Exception:
            pass

        try:
            self.view_menu.entryconfigure(0, label=t("menu.home", lang))
            self.view_menu.entryconfigure(1, label=t("menu.history", lang))
            self.view_menu.entryconfigure(2, label=t("menu.settings", lang))
        except Exception:
            pass

        try:
            # language radiobutton labels
            self.lang_menu.entryconfigure(0, label=t("menu.language.en", lang))
            self.lang_menu.entryconfigure(1, label=t("menu.language.ar", lang))
        except Exception:
            pass

        try:
            self.help_menu.entryconfigure(0, label=t("menu.about", lang))
        except Exception:
            pass

        # Toolbar - repack for direction
        ps, pso = pack_side(lang), pack_side_opposite(lang)
        for w in [self.btn_home, self.btn_history, self.btn_settings, self.toolbar_sep, self.btn_new_invoice]:
            w.pack_forget()
        self.btn_home.pack(side=ps, padx=2)
        self.btn_history.pack(side=ps, padx=2)
        self.btn_settings.pack(side=ps, padx=2)
        self.toolbar_sep.pack(side=ps, fill='y', padx=10)
        self.btn_new_invoice.pack(side=ps, padx=2)
        self.company_label.pack_forget()
        self.company_label.pack(side=pso, padx=10)
        self.btn_home.configure(text=t("toolbar.home", lang))
        self.btn_history.configure(text=t("toolbar.history", lang))
        self.btn_settings.configure(text=t("toolbar.settings", lang))
        self.btn_new_invoice.configure(text=t("toolbar.newInvoice", lang))

        # Company name: switch between stored ar/en fields
        settings = self.db.get_company_settings()
        if (lang or LANG_AR) == LANG_EN and settings.get("company_name_en"):
            self.company_label.configure(text=settings.get("company_name_en"))
        else:
            self.company_label.configure(text=settings.get("company_name_ar", "Invoice System"))

        # Notebook tabs
        try:
            self.notebook.tab(0, text=t("tab.home", lang))
            self.notebook.tab(1, text=t("tab.history", lang))
            self.notebook.tab(2, text=t("tab.settings", lang))
        except Exception:
            pass

        # Status bar
        self.statusbar.set_status(t("common.ready", lang))
        if hasattr(self.statusbar, "apply_language"):
            self.statusbar.apply_language()

        # Delegate to screens
        if hasattr(self.invoice_form, "apply_language"):
            self.invoice_form.apply_language(lang)
        if hasattr(self.invoice_history, "apply_language"):
            self.invoice_history.apply_language(lang)
        if hasattr(self.settings_screen, "apply_language"):
            self.settings_screen.apply_language(lang)

        # Update open dialogs (InvoiceView, ExportDialog, etc.)
        for d in list(self._open_dialogs):
            try:
                if d.winfo_exists() and hasattr(d, "apply_language"):
                    d.apply_language(lang)
            except (tk.TclError, AttributeError):
                if d in self._open_dialogs:
                    self._open_dialogs.remove(d)
    
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
        msg = t("msg.invoiceSavedShort", self.lang, number=invoice['invoice_number'])
        self.statusbar.set_success(msg)
        self.invoice_history.refresh()
    
    def _on_invoice_save_print(self, invoice):
        """Handle save and print"""
        msg = t("msg.invoiceSavedShort", self.lang, number=invoice['invoice_number'])
        self.statusbar.set_success(msg)
        self.invoice_history.refresh()
        self._on_view_invoice(invoice, print_mode=True)
    
    def _on_view_invoice(self, invoice, print_mode: bool = False):
        """View invoice"""
        def _unreg(d):
            try:
                if d in self._open_dialogs:
                    self._open_dialogs.remove(d)
            except (ValueError, AttributeError):
                pass
        view = InvoiceView(
            self.root, invoice, print_mode=print_mode,
            on_register=lambda d: self._open_dialogs.append(d),
            on_unregister=_unreg
        )
    
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
            t("about.title", self.lang),
            t("about.body", self.lang),
        )
    
    def _on_close(self):
        """Handle window close"""
        if messagebox.askyesno(t("exit.title", self.lang), t("exit.body", self.lang)):
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
