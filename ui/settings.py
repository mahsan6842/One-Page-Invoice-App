"""
Invoice Application - Settings Screen
Configure company info and application settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from typing import Dict, Any

from app.database import get_database
from ui.widgets import ArabicEntry, ArabicLabel, NumberEntry, FormSection


class SettingsScreen(ttk.Frame):
    """Settings configuration screen"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.db = get_database()
        
        self._create_widgets()
        self._load_settings()
    
    def _create_widgets(self):
        # Main scrollable container
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='left', fill='y')
        canvas.pack(side='right', fill='both', expand=True)
        
        # === Company Info Section ===
        company_frame = FormSection(scrollable_frame, "بيانات المؤسسة")
        company_frame.pack(fill='x', padx=10, pady=10)
        
        # Company name
        row = ttk.Frame(company_frame)
        row.pack(fill='x', pady=3)
        ttk.Label(row, text="اسم المؤسسة:", width=15, anchor='e').pack(side='right', padx=5)
        self.company_name = ArabicEntry(row, width=40)
        self.company_name.pack(side='right', padx=5, fill='x', expand=True)
        
        # Address
        row = ttk.Frame(company_frame)
        row.pack(fill='x', pady=3)
        ttk.Label(row, text="العنوان:", width=15, anchor='e').pack(side='right', padx=5)
        self.address = ArabicEntry(row, width=40)
        self.address.pack(side='right', padx=5, fill='x', expand=True)
        
        # Tax number
        row = ttk.Frame(company_frame)
        row.pack(fill='x', pady=3)
        ttk.Label(row, text="الرقم الضريبي:", width=15, anchor='e').pack(side='right', padx=5)
        self.tax_number = ArabicEntry(row, width=40)
        self.tax_number.pack(side='right', padx=5, fill='x', expand=True)
        
        # Phone 1
        row = ttk.Frame(company_frame)
        row.pack(fill='x', pady=3)
        ttk.Label(row, text="الهاتف 1:", width=15, anchor='e').pack(side='right', padx=5)
        self.phone1 = ArabicEntry(row, width=20)
        self.phone1.pack(side='right', padx=5)
        
        # Phone 2
        row = ttk.Frame(company_frame)
        row.pack(fill='x', pady=3)
        ttk.Label(row, text="الهاتف 2:", width=15, anchor='e').pack(side='right', padx=5)
        self.phone2 = ArabicEntry(row, width=20)
        self.phone2.pack(side='right', padx=5)
        
        # Logo
        row = ttk.Frame(company_frame)
        row.pack(fill='x', pady=3)
        ttk.Label(row, text="الشعار:", width=15, anchor='e').pack(side='right', padx=5)
        self.logo_path = ArabicEntry(row, width=30)
        self.logo_path.pack(side='right', padx=5)
        ttk.Button(row, text="اختيار...", command=self._browse_logo,
                  width=10).pack(side='right', padx=5)
        
        # === Invoice Settings Section ===
        invoice_frame = FormSection(scrollable_frame, "إعدادات الفاتورة")
        invoice_frame.pack(fill='x', padx=10, pady=10)
        
        # VAT rate
        row = ttk.Frame(invoice_frame)
        row.pack(fill='x', pady=3)
        ttk.Label(row, text="نسبة الضريبة (%):", width=15, anchor='e').pack(side='right', padx=5)
        self.vat_rate = NumberEntry(row, width=10)
        self.vat_rate.pack(side='right', padx=5)
        
        # Invoice prefix
        row = ttk.Frame(invoice_frame)
        row.pack(fill='x', pady=3)
        ttk.Label(row, text="بادئة رقم الفاتورة:", width=15, anchor='e').pack(side='right', padx=5)
        self.invoice_prefix = ArabicEntry(row, width=10)
        self.invoice_prefix.pack(side='right', padx=5)
        
        # Next invoice number
        row = ttk.Frame(invoice_frame)
        row.pack(fill='x', pady=3)
        ttk.Label(row, text="الرقم التالي:", width=15, anchor='e').pack(side='right', padx=5)
        self.next_number = NumberEntry(row, width=10, allow_decimal=False)
        self.next_number.pack(side='right', padx=5)
        
        # === Terms and Conditions Section ===
        terms_frame = FormSection(scrollable_frame, "الشروط والأحكام")
        terms_frame.pack(fill='x', padx=10, pady=10)
        
        self.terms_text = tk.Text(terms_frame, height=10, width=60, 
                                  wrap='word', font=('Arial', 10))
        self.terms_text.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(terms_frame, text="(أدخل كل شرط في سطر منفصل)",
                 font=('Arial', 8)).pack(anchor='e', padx=5)
        
        # === Backup Section ===
        backup_frame = FormSection(scrollable_frame, "النسخ الاحتياطي")
        backup_frame.pack(fill='x', padx=10, pady=10)
        
        btn_row = ttk.Frame(backup_frame)
        btn_row.pack(fill='x', pady=5)
        
        ttk.Button(btn_row, text="💾 إنشاء نسخة احتياطية", 
                  command=self._create_backup, width=20).pack(side='right', padx=5)
        ttk.Button(btn_row, text="📂 استعادة من نسخة", 
                  command=self._restore_backup, width=20).pack(side='right', padx=5)
        
        self.backup_label = ttk.Label(backup_frame, text="")
        self.backup_label.pack(anchor='e', pady=5)
        
        # === Action Buttons ===
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill='x', padx=10, pady=20)
        
        ttk.Button(btn_frame, text="💾 حفظ الإعدادات", 
                  command=self._save_settings, width=15).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="🔄 إعادة تحميل", 
                  command=self._load_settings, width=15).pack(side='right', padx=5)
    
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
            
            messagebox.showinfo("نجاح", "تم حفظ الإعدادات بنجاح")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ الإعدادات: {str(e)}")
    
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
                messagebox.showinfo("نجاح", f"تم إنشاء النسخة الاحتياطية:\n{filepath}")
            else:
                self.backup_label.configure(text="✗ فشل إنشاء النسخة")
                messagebox.showerror("خطأ", "فشل إنشاء النسخة الاحتياطية")
    
    def _restore_backup(self):
        """Restore from backup"""
        filepath = filedialog.askopenfilename(
            filetypes=[('Database files', '*.db')]
        )
        
        if filepath:
            if messagebox.askyesno("تأكيد", 
                "سيتم استبدال قاعدة البيانات الحالية.\n"
                "هل أنت متأكد من المتابعة؟"):
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
                    messagebox.showinfo("نجاح", "تم استعادة النسخة الاحتياطية بنجاح")
                except Exception as e:
                    self.backup_label.configure(text="✗ فشل الاستعادة")
                    messagebox.showerror("خطأ", f"فشلت الاستعادة: {str(e)}")
    
    def _get_date_string(self) -> str:
        """Get current date as string"""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
