"""
Invoice Application - Settings Screen
Configure company info and application settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from typing import Dict, Any

from app.database import get_database
from app.i18n import LANG_AR, LANG_EN, t, get_current_lang, pack_side, pack_side_opposite, anchor_for
from ui.widgets import ArabicEntry, ArabicLabel, NumberEntry, FormSection, apply_direction_recursive


class SettingsScreen(ttk.Frame):
    """Settings configuration screen"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.db = get_database()
        self.lang = get_current_lang() or LANG_AR
        
        self._create_widgets()
        self._load_settings()
    
    def _create_widgets(self):
        ps, pso = pack_side(self.lang), pack_side_opposite(self.lang)
        self.settings_canvas = tk.Canvas(self, highlightthickness=0)
        self.settings_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.settings_canvas.yview)
        canvas = self.settings_canvas
        scrollbar = self.settings_scrollbar
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        self.settings_canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', self._on_canvas_configure)
        scrollbar.pack(side=pso, fill='y')
        canvas.pack(side=ps, fill='both', expand=True)
        
        # === Company Info Section ===
        self.company_frame = FormSection(scrollable_frame, "بيانات المؤسسة")
        self.company_frame.pack(fill='x', padx=10, pady=10)
        
        # Company name
        row = ttk.Frame(self.company_frame)
        row.pack(fill='x', pady=3)
        self.lbl_company_name = ttk.Label(row, text="اسم المؤسسة:", width=15, anchor=anchor_for(self.lang))
        self.lbl_company_name.pack(side=ps, padx=5)
        self.company_name = ArabicEntry(row, width=40)
        self.company_name.pack(side=ps, padx=5, fill='x', expand=True)
        
        # Address
        row = ttk.Frame(self.company_frame)
        row.pack(fill='x', pady=3)
        self.lbl_address = ttk.Label(row, text="العنوان:", width=15, anchor=anchor_for(self.lang))
        self.lbl_address.pack(side=ps, padx=5)
        self.address = ArabicEntry(row, width=40)
        self.address.pack(side=ps, padx=5, fill='x', expand=True)
        
        # Tax number
        row = ttk.Frame(self.company_frame)
        row.pack(fill='x', pady=3)
        self.lbl_tax_number = ttk.Label(row, text="الرقم الضريبي:", width=15, anchor=anchor_for(self.lang))
        self.lbl_tax_number.pack(side=ps, padx=5)
        self.tax_number = ArabicEntry(row, width=40)
        self.tax_number.pack(side=ps, padx=5, fill='x', expand=True)
        
        row = ttk.Frame(self.company_frame)
        row.pack(fill='x', pady=3)
        self.lbl_phone1 = ttk.Label(row, text="الهاتف 1:", width=15, anchor=anchor_for(self.lang))
        self.lbl_phone1.pack(side=ps, padx=5)
        self.phone1 = ArabicEntry(row, width=20)
        self.phone1.pack(side=ps, padx=5)
        
        row = ttk.Frame(self.company_frame)
        row.pack(fill='x', pady=3)
        self.lbl_phone2 = ttk.Label(row, text="الهاتف 2:", width=15, anchor=anchor_for(self.lang))
        self.lbl_phone2.pack(side=ps, padx=5)
        self.phone2 = ArabicEntry(row, width=20)
        self.phone2.pack(side=ps, padx=5)
        
        row = ttk.Frame(self.company_frame)
        row.pack(fill='x', pady=3)
        self.lbl_logo = ttk.Label(row, text="الشعار:", width=15, anchor=anchor_for(self.lang))
        self.lbl_logo.pack(side=ps, padx=5)
        self.logo_path = ArabicEntry(row, width=30)
        self.logo_path.pack(side=ps, padx=5)
        self.btn_browse_logo = ttk.Button(row, text="اختيار...", command=self._browse_logo, width=10)
        self.btn_browse_logo.pack(side=ps, padx=5)
        
        self.invoice_frame = FormSection(scrollable_frame, "إعدادات الفاتورة")
        self.invoice_frame.pack(fill='x', padx=10, pady=10)
        
        row = ttk.Frame(self.invoice_frame)
        row.pack(fill='x', pady=3)
        self.lbl_vat_rate = ttk.Label(row, text="نسبة الضريبة (%):", width=15, anchor=anchor_for(self.lang))
        self.lbl_vat_rate.pack(side=ps, padx=5)
        self.vat_rate = NumberEntry(row, width=10)
        self.vat_rate.pack(side=ps, padx=5)
        
        row = ttk.Frame(self.invoice_frame)
        row.pack(fill='x', pady=3)
        self.lbl_invoice_prefix = ttk.Label(row, text="بادئة رقم الفاتورة:", width=15, anchor=anchor_for(self.lang))
        self.lbl_invoice_prefix.pack(side=ps, padx=5)
        self.invoice_prefix = ArabicEntry(row, width=10)
        self.invoice_prefix.pack(side=ps, padx=5)
        
        row = ttk.Frame(self.invoice_frame)
        row.pack(fill='x', pady=3)
        self.lbl_next_number = ttk.Label(row, text="الرقم التالي:", width=15, anchor=anchor_for(self.lang))
        self.lbl_next_number.pack(side=ps, padx=5)
        self.next_number = NumberEntry(row, width=10, allow_decimal=False)
        self.next_number.pack(side=ps, padx=5)
        
        # === Terms and Conditions Section ===
        self.terms_frame = FormSection(scrollable_frame, "الشروط والأحكام")
        self.terms_frame.pack(fill='x', padx=10, pady=10)
        
        self.terms_text = tk.Text(self.terms_frame, height=10, width=60,
                                  wrap='word', font=('Arial', 10))
        self.terms_text.pack(fill='x', padx=5, pady=5)
        
        self.lbl_terms_hint = ttk.Label(self.terms_frame, text="(أدخل كل شرط في سطر منفصل)", font=('Arial', 8))
        self.lbl_terms_hint.pack(anchor=anchor_for(self.lang), padx=5)
        
        # === Backup Section ===
        self.backup_frame = FormSection(scrollable_frame, "النسخ الاحتياطي")
        self.backup_frame.pack(fill='x', padx=10, pady=10)
        
        btn_row = ttk.Frame(self.backup_frame)
        btn_row.pack(fill='x', pady=5)
        
        self.btn_row = btn_row
        self.btn_create_backup = ttk.Button(btn_row, text="💾 إنشاء نسخة احتياطية",
                                            command=self._create_backup, width=20)
        self.btn_create_backup.pack(side=ps, padx=5)
        self.btn_restore_backup = ttk.Button(btn_row, text="📂 استعادة من نسخة",
                                             command=self._restore_backup, width=20)
        self.btn_restore_backup.pack(side=ps, padx=5)
        self.backup_label = ttk.Label(self.backup_frame, text="")
        self.backup_label.pack(anchor=anchor_for(self.lang), pady=5)
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill='x', padx=10, pady=20)
        self.btn_save = ttk.Button(btn_frame, text="💾 حفظ الإعدادات",
                                   command=self._save_settings, width=15)
        self.btn_save.pack(side=ps, padx=5)
        self.btn_reload = ttk.Button(btn_frame, text="🔄 إعادة تحميل",
                                     command=self._load_settings, width=15)
        self.btn_reload.pack(side=ps, padx=5)
    
    def _on_canvas_configure(self, event=None):
        """Resize inner frame when canvas resizes."""
        if event and hasattr(self, 'settings_canvas_window'):
            self.settings_canvas.itemconfig(self.settings_canvas_window, width=event.width)

    def _load_settings(self):
        """Load settings from database"""
        settings = self.db.get_company_settings()
        
        # Company info
        self._set_entry(self.company_name, settings.get('company_name_ar', ''))
        self._set_entry(self.address, settings.get('address_ar', ''))
        self._set_entry(self.tax_number, settings.get('tax_number', ''))
        self._set_entry(self.phone1, settings.get('phone1', ''))
        self._set_entry(self.phone2, settings.get('phone2', ''))
        self._set_entry(self.logo_path, settings.get('logo_path', ''))
        
        # Invoice settings
        vat = settings.get('vat_rate', 0.15) * 100  # Convert to percentage
        self._set_entry(self.vat_rate, str(int(vat)))
        self._set_entry(self.invoice_prefix, settings.get('invoice_prefix', '2024'))
        self._set_entry(self.next_number, str(settings.get('next_invoice_number', 100001)))
        
        # Terms
        terms = settings.get('terms_conditions', [])
        if isinstance(terms, list):
            self.terms_text.delete('1.0', tk.END)
            self.terms_text.insert('1.0', '\n'.join(terms))
    
    def _set_entry(self, entry, value: str):
        """Set entry value"""
        entry.delete(0, tk.END)
        entry.insert(0, value)
    
    def _save_settings(self):
        """Save settings to database"""
        try:
            # Get terms as list
            terms_text = self.terms_text.get('1.0', tk.END).strip()
            terms_list = [line.strip() for line in terms_text.split('\n') if line.strip()]
            
            # Get VAT rate as decimal
            vat_percent = float(self.vat_rate.get() or 15)
            vat_decimal = vat_percent / 100
            
            # Update settings
            self.db.update_company_settings(
                company_name_ar=self.company_name.get(),
                address_ar=self.address.get(),
                tax_number=self.tax_number.get(),
                phone1=self.phone1.get(),
                phone2=self.phone2.get(),
                logo_path=self.logo_path.get(),
                vat_rate=vat_decimal,
                invoice_prefix=self.invoice_prefix.get(),
                next_invoice_number=int(self.next_number.get() or 100001),
                terms_conditions=terms_list
            )
            
            messagebox.showinfo(t("common.success", self.lang), t("msg.settingsSaved", self.lang))
            
        except Exception as e:
            msg = t("msg.settingsSaveFailed", self.lang, error=str(e))
            messagebox.showerror(t("common.error", self.lang), msg)
    
    def _browse_logo(self):
        """Browse for logo image"""
        filepath = filedialog.askopenfilename(
            filetypes=[
                ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp'),
                ('All files', '*.*')
            ]
        )
        if filepath:
            self._set_entry(self.logo_path, filepath)
    
    def _create_backup(self):
        """Create database backup"""
        filepath = filedialog.asksaveasfilename(
            defaultextension='.db',
            filetypes=[('Database files', '*.db')],
            initialfile=f'invoices_backup_{self._get_date_string()}.db'
        )
        
        if filepath:
            if self.db.backup(filepath):
                self.backup_label.configure(text=f"✓ تم إنشاء النسخة الاحتياطية")
                messagebox.showinfo(t("common.success", self.lang), t("msg.backupCreated", self.lang, path=filepath))
            else:
                self.backup_label.configure(text="✗ فشل إنشاء النسخة")
                messagebox.showerror(t("common.error", self.lang),
                                     t("msg.backupFailed", self.lang))
    
    def _restore_backup(self):
        """Restore from backup"""
        filepath = filedialog.askopenfilename(
            filetypes=[('Database files', '*.db')]
        )
        
        if filepath:
            confirm_msg = t("msg.confirmRestore", self.lang)
            if messagebox.askyesno(t("common.confirm", self.lang), confirm_msg):
                try:
                    import shutil
                    # Close current connection
                    self.db.close()
                    # Copy backup file
                    shutil.copy(filepath, self.db.db_path)
                    # Reconnect
                    self.db.connect()
                    self._load_settings()
                    
                    self.backup_label.configure(text="✓ تم استعادة النسخة الاحتياطية")
                    messagebox.showinfo(t("common.success", self.lang), t("msg.restoreSuccess", self.lang))
                except Exception as e:
                    self.backup_label.configure(text="✗ فشل الاستعادة")
                    msg = t("msg.restoreFailed", self.lang, error=str(e))
                    messagebox.showerror(t("common.error", self.lang), msg)

    def apply_language(self, lang: str):
        """Apply language to Settings UI."""
        self.lang = lang or LANG_AR

        self.company_frame.configure(text=t("settings.companyInfo", self.lang))
        self.lbl_company_name.configure(text=t("settings.companyName", self.lang))
        self.lbl_address.configure(text=t("settings.address", self.lang))
        self.lbl_tax_number.configure(text=t("settings.taxNumber", self.lang))
        self.lbl_phone1.configure(text=t("settings.phone1", self.lang))
        self.lbl_phone2.configure(text=t("settings.phone2", self.lang))
        self.lbl_logo.configure(text=t("settings.logo", self.lang))
        self.btn_browse_logo.configure(text=t("settings.browse", self.lang))

        self.invoice_frame.configure(text=t("settings.invoiceSettings", self.lang))
        self.lbl_vat_rate.configure(text=t("settings.vatRate", self.lang))
        self.lbl_invoice_prefix.configure(text=t("settings.invoicePrefix", self.lang))
        self.lbl_next_number.configure(text=t("settings.nextNumber", self.lang))

        self.terms_frame.configure(text=t("settings.termsConditions", self.lang))
        self.lbl_terms_hint.configure(text=t("settings.termsHint", self.lang))

        self.backup_frame.configure(text=t("settings.backup", self.lang))
        self.btn_create_backup.configure(text=t("settings.createBackup", self.lang))
        self.btn_restore_backup.configure(text=t("settings.restoreBackup", self.lang))

        self.btn_save.configure(text=t("settings.saveSettings", self.lang))
        self.btn_reload.configure(text=t("settings.reload", self.lang))

        # Repack form rows for direction
        ps = pack_side(self.lang)
        for w in [self.lbl_company_name, self.company_name]:
            w.pack_forget()
        self.lbl_company_name.pack(side=ps, padx=5)
        self.company_name.pack(side=ps, padx=5, fill='x', expand=True)
        for w in [self.lbl_address, self.address]:
            w.pack_forget()
        self.lbl_address.pack(side=ps, padx=5)
        self.address.pack(side=ps, padx=5, fill='x', expand=True)
        for w in [self.lbl_tax_number, self.tax_number]:
            w.pack_forget()
        self.lbl_tax_number.pack(side=ps, padx=5)
        self.tax_number.pack(side=ps, padx=5, fill='x', expand=True)
        for w in [self.lbl_phone1, self.phone1]:
            w.pack_forget()
        self.lbl_phone1.pack(side=ps, padx=5)
        self.phone1.pack(side=ps, padx=5)
        for w in [self.lbl_phone2, self.phone2]:
            w.pack_forget()
        self.lbl_phone2.pack(side=ps, padx=5)
        self.phone2.pack(side=ps, padx=5)
        for w in [self.lbl_logo, self.logo_path, self.btn_browse_logo]:
            w.pack_forget()
        self.lbl_logo.pack(side=ps, padx=5)
        self.logo_path.pack(side=ps, padx=5)
        self.btn_browse_logo.pack(side=ps, padx=5)
        for w in [self.lbl_vat_rate, self.vat_rate]:
            w.pack_forget()
        self.lbl_vat_rate.pack(side=ps, padx=5)
        self.vat_rate.pack(side=ps, padx=5)
        for w in [self.lbl_invoice_prefix, self.invoice_prefix]:
            w.pack_forget()
        self.lbl_invoice_prefix.pack(side=ps, padx=5)
        self.invoice_prefix.pack(side=ps, padx=5)
        for w in [self.lbl_next_number, self.next_number]:
            w.pack_forget()
        self.lbl_next_number.pack(side=ps, padx=5)
        self.next_number.pack(side=ps, padx=5)

        anch = anchor_for(self.lang)
        for lbl in [self.lbl_company_name, self.lbl_address, self.lbl_tax_number,
                    self.lbl_phone1, self.lbl_phone2, self.lbl_logo,
                    self.lbl_vat_rate, self.lbl_invoice_prefix, self.lbl_next_number]:
            lbl.configure(anchor=anch)
        self.lbl_terms_hint.pack_forget()
        self.lbl_terms_hint.pack(anchor=anch, padx=5)
        self.backup_label.pack_forget()
        self.backup_label.pack(anchor=anch, pady=5)

        # Repack buttons for direction
        ps = pack_side(self.lang)
        for w in [self.btn_create_backup, self.btn_restore_backup]:
            w.pack_forget()
        self.btn_create_backup.pack(side=ps, padx=5)
        self.btn_restore_backup.pack(side=ps, padx=5)
        for w in [self.btn_save, self.btn_reload]:
            w.pack_forget()
        self.btn_save.pack(side=ps, padx=5)
        self.btn_reload.pack(side=ps, padx=5)

        pso = pack_side_opposite(self.lang)
        self.settings_scrollbar.pack_forget()
        self.settings_canvas.pack_forget()
        self.settings_scrollbar.pack(side=pso, fill='y')
        self.settings_canvas.pack(side=ps, fill='both', expand=True)

        apply_direction_recursive(self, self.lang)
    
    def _get_date_string(self) -> str:
        """Get current date as string"""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
