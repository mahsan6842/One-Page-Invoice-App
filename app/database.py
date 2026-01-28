"""
Invoice Application - Database Module
Handles all SQLite database operations
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import json


class Database:
    """SQLite database handler for invoice application"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            # Default path in data folder
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'invoices.db')
        
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
        self._migrate_schema()
        self.initialize_default_settings()
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create all required tables"""
        cursor = self.conn.cursor()
        
        # Company Settings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_settings (
                id INTEGER PRIMARY KEY DEFAULT 1,
                company_name_ar TEXT NOT NULL DEFAULT 'اسم المؤسسة',
                company_name_en TEXT DEFAULT '',
                address_ar TEXT DEFAULT '',
                address_en TEXT DEFAULT '',
                tax_number TEXT NOT NULL DEFAULT '',
                phone1 TEXT DEFAULT '',
                phone2 TEXT DEFAULT '',
                logo_path TEXT DEFAULT '',
                vat_rate REAL DEFAULT 0.15,
                invoice_prefix TEXT DEFAULT '2024',
                next_invoice_number INTEGER DEFAULT 100001,
                terms_conditions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Customers Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_ar TEXT NOT NULL,
                name_en TEXT DEFAULT '',
                tax_number TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                address TEXT DEFAULT '',
                email TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Invoices Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                invoice_date DATE NOT NULL,
                invoice_time TIME DEFAULT (time('now', 'localtime')),
                customer_id INTEGER,
                customer_name TEXT DEFAULT '',
                customer_tax_number TEXT DEFAULT '',
                customer_phone TEXT DEFAULT '',
                customer_address TEXT DEFAULT '',
                payment_type TEXT DEFAULT 'نقدا',
                salesperson TEXT DEFAULT 'admin',
                subtotal REAL NOT NULL DEFAULT 0,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                taxable_amount REAL NOT NULL DEFAULT 0,
                tax_amount REAL NOT NULL DEFAULT 0,
                net_total REAL NOT NULL DEFAULT 0,
                notes TEXT DEFAULT '',
                status TEXT DEFAULT 'active',
                qr_code_data TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        # Invoice Items Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                item_barcode TEXT DEFAULT '',
                unit TEXT DEFAULT 'حبة',
                quantity REAL NOT NULL DEFAULT 1,
                unit_price REAL NOT NULL DEFAULT 0,
                total_price REAL NOT NULL DEFAULT 0,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                tax_amount REAL NOT NULL DEFAULT 0,
                net_amount REAL NOT NULL DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
            )
        """)
        
        # Products Table (for autocomplete)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name_ar TEXT NOT NULL,
                name_en TEXT DEFAULT '',
                unit TEXT DEFAULT 'حبة',
                default_price REAL DEFAULT 0,
                category TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice ON invoice_items(invoice_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name_ar)")
        
        self.conn.commit()

    def _migrate_schema(self):
        """
        Lightweight schema migrations for existing databases.
        Keep this backward compatible and safe to run at every startup.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(company_settings)")
            cols = {row[1] for row in cursor.fetchall()}  # row[1] = name

            if "ui_language" not in cols:
                cursor.execute("ALTER TABLE company_settings ADD COLUMN ui_language TEXT DEFAULT 'ar'")

            self.conn.commit()
        except Exception as e:
            # Don't hard-fail startup on migration issues
            print(f"Schema migration warning: {e}")
    
    def initialize_default_settings(self):
        """Initialize default company settings if not exists"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM company_settings")
        if cursor.fetchone()[0] == 0:
            # Insert default settings based on the invoice
            default_terms = json.dumps([
                "يدفع الزبون 50% من قيمة الفاتورة خلال توقيع العقد",
                "عند انتهاء المحلات من التصنيع يلتزم الزبون بتسديد كامل المبلغ قبل التركيب بيومين",
                "يتم تركيب الرخام بعد الانتهاء من اعمال المطبخ لمدة تتراوح من يومين لاربعة ايام",
                "اعمال السباكة والكهرباء على العميل - المعرض غير مسؤول عنها",
                "على العميل ازالة اي اعمال السباكة او الكهرباء قبل التركيب",
                "الفني غير مسؤول عن اي خلل يحصل للسباكة والكهرباء اثناء التركيب",
                "المعرض غير مسؤول عن المطابخ والدو لب بعد مضي 45 يوم من تاريخ التركيب باستثناء الضمان المحدد بالا علي",
                "المحل غير مسؤول عن العربون بعد البدء في القص والعميل يتحمل اي فرق في التغيير بالالوان او المقاسات والعربون غير مسترد بعد البدء في الاعمال"
            ], ensure_ascii=False)
            
            cursor.execute("""
                INSERT INTO company_settings 
                (company_name_ar, address_ar, tax_number, phone1, phone2, terms_conditions, ui_language)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "مؤسسة التفرد الاصيل للمطابخ",
                "بريدة - طريق الملك فيصل - حي العجيبة",
                "300694858900003",
                "0591650315",
                "0580911269",
                default_terms,
                "ar",
            ))
            self.conn.commit()
    
    # ==================== Company Settings ====================
    
    def get_company_settings(self) -> Dict[str, Any]:
        """Get company settings"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM company_settings WHERE id = 1")
        row = cursor.fetchone()
        if row:
            settings = dict(row)
            # Parse terms_conditions JSON
            if settings.get('terms_conditions'):
                try:
                    settings['terms_conditions'] = json.loads(settings['terms_conditions'])
                except:
                    settings['terms_conditions'] = []
            return settings
        return {}
    
    def update_company_settings(self, **kwargs) -> bool:
        """Update company settings"""
        cursor = self.conn.cursor()
        
        # Convert terms_conditions to JSON if present
        if 'terms_conditions' in kwargs and isinstance(kwargs['terms_conditions'], list):
            kwargs['terms_conditions'] = json.dumps(kwargs['terms_conditions'], ensure_ascii=False)
        
        # Build update query dynamically
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        if fields:
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(1)  # WHERE id = 1
            
            query = f"UPDATE company_settings SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            self.conn.commit()
            return True
        return False
    
    def get_next_invoice_number(self) -> str:
        """Get and increment next invoice number"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT invoice_prefix, next_invoice_number FROM company_settings WHERE id = 1")
        row = cursor.fetchone()
        
        prefix = row['invoice_prefix'] if row else '2024'
        number = row['next_invoice_number'] if row else 100001
        
        invoice_number = f"{prefix}{number}"
        
        # Increment for next time
        cursor.execute("""
            UPDATE company_settings 
            SET next_invoice_number = next_invoice_number + 1 
            WHERE id = 1
        """)
        self.conn.commit()
        
        return invoice_number
    
    # ==================== Customers ====================
    
    def add_customer(self, name_ar: str, **kwargs) -> int:
        """Add new customer"""
        cursor = self.conn.cursor()
        
        fields = ['name_ar']
        values = [name_ar]
        
        for key in ['name_en', 'tax_number', 'phone', 'address', 'email', 'notes']:
            if key in kwargs:
                fields.append(key)
                values.append(kwargs[key])
        
        placeholders = ', '.join(['?' for _ in values])
        query = f"INSERT INTO customers ({', '.join(fields)}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.lastrowid
    
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def search_customers(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search customers by name or phone"""
        cursor = self.conn.cursor()
        search_pattern = f"%{search_term}%"
        cursor.execute("""
            SELECT * FROM customers 
            WHERE name_ar LIKE ? OR phone LIKE ? OR tax_number LIKE ?
            ORDER BY name_ar
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_customers(self) -> List[Dict[str, Any]]:
        """Get all customers"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM customers ORDER BY name_ar")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_customer(self, customer_id: int, **kwargs) -> bool:
        """Update customer"""
        cursor = self.conn.cursor()
        
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        if fields:
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(customer_id)
            
            query = f"UPDATE customers SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            self.conn.commit()
            return True
        return False
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete customer"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ==================== Invoices ====================
    
    def create_invoice(self, invoice_data: Dict[str, Any], items: List[Dict[str, Any]]) -> int:
        """Create new invoice with items"""
        cursor = self.conn.cursor()
        
        # Generate invoice number if not provided
        if 'invoice_number' not in invoice_data:
            invoice_data['invoice_number'] = self.get_next_invoice_number()
        
        # Set date if not provided
        if 'invoice_date' not in invoice_data:
            invoice_data['invoice_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Insert invoice
        invoice_fields = [
            'invoice_number', 'invoice_date', 'customer_id', 'customer_name',
            'customer_tax_number', 'customer_phone', 'customer_address',
            'payment_type', 'salesperson', 'subtotal', 'discount_percent',
            'discount_amount', 'taxable_amount', 'tax_amount', 'net_total',
            'notes', 'qr_code_data'
        ]
        
        fields = []
        values = []
        for field in invoice_fields:
            if field in invoice_data:
                fields.append(field)
                values.append(invoice_data[field])
        
        placeholders = ', '.join(['?' for _ in values])
        query = f"INSERT INTO invoices ({', '.join(fields)}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        invoice_id = cursor.lastrowid
        
        # Insert items
        for idx, item in enumerate(items):
            item['invoice_id'] = invoice_id
            item['sort_order'] = idx
            
            item_fields = [
                'invoice_id', 'item_name', 'item_barcode', 'unit',
                'quantity', 'unit_price', 'total_price', 'discount_percent',
                'discount_amount', 'tax_amount', 'net_amount', 'sort_order'
            ]
            
            i_fields = []
            i_values = []
            for field in item_fields:
                if field in item:
                    i_fields.append(field)
                    i_values.append(item[field])
            
            i_placeholders = ', '.join(['?' for _ in i_values])
            i_query = f"INSERT INTO invoice_items ({', '.join(i_fields)}) VALUES ({i_placeholders})"
            cursor.execute(i_query, i_values)
        
        self.conn.commit()
        return invoice_id
    
    def get_invoice(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Get invoice by ID with items"""
        cursor = self.conn.cursor()
        
        # Get invoice
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        invoice = dict(row)
        
        # Get items
        cursor.execute("""
            SELECT * FROM invoice_items 
            WHERE invoice_id = ? 
            ORDER BY sort_order
        """, (invoice_id,))
        invoice['items'] = [dict(item) for item in cursor.fetchall()]
        
        return invoice
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get invoice by invoice number"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM invoices WHERE invoice_number = ?", (invoice_number,))
        row = cursor.fetchone()
        if row:
            return self.get_invoice(row['id'])
        return None
    
    def get_invoices(self, page: int = 1, per_page: int = 50, 
                     start_date: str = None, end_date: str = None,
                     search_term: str = None) -> List[Dict[str, Any]]:
        """Get paginated list of invoices"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM invoices WHERE status = 'active'"
        params = []
        
        if start_date:
            query += " AND invoice_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND invoice_date <= ?"
            params.append(end_date)
        
        if search_term:
            query += " AND (invoice_number LIKE ? OR customer_name LIKE ?)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern])
        
        query += " ORDER BY id DESC"
        query += f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_invoices_count(self, start_date: str = None, end_date: str = None,
                           search_term: str = None) -> int:
        """Get total count of invoices"""
        cursor = self.conn.cursor()
        
        query = "SELECT COUNT(*) FROM invoices WHERE status = 'active'"
        params = []
        
        if start_date:
            query += " AND invoice_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND invoice_date <= ?"
            params.append(end_date)
        
        if search_term:
            query += " AND (invoice_number LIKE ? OR customer_name LIKE ?)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern])
        
        cursor.execute(query, params)
        return cursor.fetchone()[0]
    
    def get_invoices_total(self, start_date: str = None, end_date: str = None) -> float:
        """Get total amount of invoices"""
        cursor = self.conn.cursor()
        
        query = "SELECT COALESCE(SUM(net_total), 0) FROM invoices WHERE status = 'active'"
        params = []
        
        if start_date:
            query += " AND invoice_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND invoice_date <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        return cursor.fetchone()[0]
    
    def cancel_invoice(self, invoice_id: int) -> bool:
        """Cancel an invoice (soft delete)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE invoices 
            SET status = 'cancelled', updated_at = ? 
            WHERE id = ?
        """, (datetime.now().isoformat(), invoice_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """Permanently delete an invoice"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ==================== Products ====================
    
    def add_product(self, name_ar: str, **kwargs) -> int:
        """Add new product"""
        cursor = self.conn.cursor()
        
        fields = ['name_ar']
        values = [name_ar]
        
        for key in ['barcode', 'name_en', 'unit', 'default_price', 'category']:
            if key in kwargs:
                fields.append(key)
                values.append(kwargs[key])
        
        placeholders = ', '.join(['?' for _ in values])
        query = f"INSERT INTO products ({', '.join(fields)}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.lastrowid
    
    def search_products(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search products by name or barcode"""
        cursor = self.conn.cursor()
        search_pattern = f"%{search_term}%"
        cursor.execute("""
            SELECT * FROM products 
            WHERE is_active = 1 AND (name_ar LIKE ? OR barcode LIKE ?)
            ORDER BY name_ar
            LIMIT ?
        """, (search_pattern, search_pattern, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Backup ====================
    
    def backup(self, backup_path: str) -> bool:
        """Create database backup"""
        import shutil
        try:
            # Close connection temporarily
            self.conn.close()
            shutil.copy(self.db_path, backup_path)
            self.connect()
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            self.connect()
            return False


# Singleton instance
_db_instance = None

def get_database() -> Database:
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


if __name__ == "__main__":
    # Test database
    db = get_database()
    print("Database initialized successfully!")
    print(f"Database path: {db.db_path}")
    
    # Test settings
    settings = db.get_company_settings()
    print(f"Company: {settings.get('company_name_ar')}")
    
    # Test invoice number
    inv_num = db.get_next_invoice_number()
    print(f"Next invoice number: {inv_num}")
