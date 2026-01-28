"""
Invoice Application - Invoice Logic
Business logic for invoice calculations and validation
"""

from datetime import datetime
from typing import Dict, List, Any, Tuple


class InvoiceCalculator:
    """Handles all invoice calculations"""
    
    def __init__(self, vat_rate: float = 0.15):
        """
        Initialize calculator with VAT rate
        
        Args:
            vat_rate: VAT rate as decimal (0.15 for 15%)
        """
        self.vat_rate = vat_rate
    
    def calculate_item(
        self,
        unit_price: float,
        quantity: float,
        discount_percent: float = 0
    ) -> Dict[str, float]:
        """
        Calculate single item amounts
        
        Args:
            unit_price: Price per unit
            quantity: Number of units
            discount_percent: Discount percentage (0-100)
            
        Returns:
            Dictionary with total_price, discount_amount, tax_amount, net_amount
        """
        # Calculate total before discount
        total_price = unit_price * quantity
        
        # Calculate discount
        discount_amount = total_price * (discount_percent / 100)
        
        # Taxable amount after discount
        taxable = total_price - discount_amount
        
        # Calculate VAT
        tax_amount = taxable * self.vat_rate
        
        # Net amount including VAT
        net_amount = taxable + tax_amount
        
        return {
            'total_price': round(total_price, 2),
            'discount_amount': round(discount_amount, 2),
            'tax_amount': round(tax_amount, 2),
            'net_amount': round(net_amount, 2)
        }
    
    def calculate_invoice(
        self,
        items: List[Dict[str, Any]],
        global_discount_percent: float = 0
    ) -> Dict[str, float]:
        """
        Calculate invoice totals from items
        
        Args:
            items: List of item dictionaries with unit_price, quantity
            global_discount_percent: Additional discount on entire invoice
            
        Returns:
            Dictionary with subtotal, discount_amount, taxable_amount, tax_amount, net_total
        """
        # Calculate each item
        processed_items = []
        subtotal = 0
        total_item_discounts = 0
        
        for item in items:
            calc = self.calculate_item(
                item.get('unit_price', 0),
                item.get('quantity', 1),
                item.get('discount_percent', 0)
            )
            
            subtotal += calc['total_price']
            total_item_discounts += calc['discount_amount']
            
            processed_items.append({**item, **calc})
        
        # Apply global discount
        subtotal_after_item_discounts = subtotal - total_item_discounts
        global_discount_amount = subtotal_after_item_discounts * (global_discount_percent / 100)
        
        # Total discount
        total_discount = total_item_discounts + global_discount_amount
        
        # Taxable amount
        taxable_amount = subtotal - total_discount
        
        # VAT
        tax_amount = taxable_amount * self.vat_rate
        
        # Net total
        net_total = taxable_amount + tax_amount
        
        return {
            'subtotal': round(subtotal, 2),
            'discount_percent': global_discount_percent,
            'discount_amount': round(total_discount, 2),
            'taxable_amount': round(taxable_amount, 2),
            'tax_amount': round(tax_amount, 2),
            'net_total': round(net_total, 2),
            'items': processed_items
        }
    
    def recalculate_from_net(self, net_total: float) -> Dict[str, float]:
        """
        Reverse calculate from net total (for price validation)
        
        Args:
            net_total: Total including VAT
            
        Returns:
            Dictionary with taxable_amount, tax_amount
        """
        taxable = net_total / (1 + self.vat_rate)
        tax = net_total - taxable
        
        return {
            'taxable_amount': round(taxable, 2),
            'tax_amount': round(tax, 2)
        }


class InvoiceValidator:
    """Validates invoice data"""
    
    @staticmethod
    def validate_item(item: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate single item
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not item.get('item_name', '').strip():
            return False, "اسم الصنف مطلوب"
        
        quantity = item.get('quantity', 0)
        if quantity <= 0:
            return False, "الكمية يجب أن تكون أكبر من صفر"
        
        unit_price = item.get('unit_price', 0)
        if unit_price < 0:
            return False, "السعر لا يمكن أن يكون سالباً"
        
        discount = item.get('discount_percent', 0)
        if discount < 0 or discount > 100:
            return False, "نسبة الخصم يجب أن تكون بين 0 و 100"
        
        return True, ""
    
    @staticmethod
    def validate_invoice(invoice_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete invoice
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check for items
        items = invoice_data.get('items', [])
        if not items:
            errors.append("الفاتورة يجب أن تحتوي على صنف واحد على الأقل")
        
        # Validate each item
        for i, item in enumerate(items, 1):
            valid, msg = InvoiceValidator.validate_item(item)
            if not valid:
                errors.append(f"الصنف {i}: {msg}")
        
        # Check totals
        if invoice_data.get('net_total', 0) < 0:
            errors.append("إجمالي الفاتورة لا يمكن أن يكون سالباً")
        
        # Check discount
        discount = invoice_data.get('discount_percent', 0)
        if discount < 0 or discount > 100:
            errors.append("نسبة الخصم يجب أن تكون بين 0 و 100")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_customer(customer_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate customer data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        name = customer_data.get('name_ar', '').strip()
        if not name:
            return False, "اسم العميل مطلوب"
        
        # Validate Saudi phone number format (optional)
        phone = customer_data.get('phone', '').strip()
        if phone:
            # Remove spaces and dashes
            phone_clean = phone.replace(' ', '').replace('-', '')
            if phone_clean and not phone_clean.startswith(('05', '5', '+9665')):
                return False, "رقم الهاتف غير صحيح"
        
        return True, ""


def format_saudi_number(number: float, currency: bool = True) -> str:
    """
    Format number in Saudi style
    
    Args:
        number: Number to format
        currency: Whether to append currency symbol
        
    Returns:
        Formatted string
    """
    formatted = f"{number:,.2f}"
    if currency:
        formatted += " ريال"
    return formatted


def parse_number(text: str) -> float:
    """
    Parse number from text, handling Arabic numerals
    
    Args:
        text: Text to parse
        
    Returns:
        Parsed float
    """
    if not text:
        return 0.0
    
    # Arabic to Western numeral mapping
    arabic_numerals = '٠١٢٣٤٥٦٧٨٩'
    western_numerals = '0123456789'
    
    # Convert Arabic numerals
    for ar, en in zip(arabic_numerals, western_numerals):
        text = text.replace(ar, en)
    
    # Remove commas and spaces
    text = text.replace(',', '').replace(' ', '').strip()
    
    try:
        return float(text)
    except ValueError:
        return 0.0


def generate_invoice_number(prefix: str, last_number: int) -> str:
    """
    Generate next invoice number
    
    Args:
        prefix: Year prefix (e.g., '2024')
        last_number: Last used number
        
    Returns:
        New invoice number string
    """
    return f"{prefix}{last_number + 1}"


def get_current_datetime() -> Tuple[str, str]:
    """
    Get current date and time in invoice format
    
    Returns:
        Tuple of (date_string, time_string)
    """
    now = datetime.now()
    return (
        now.strftime('%Y-%m-%d'),
        now.strftime('%H:%M:%S')
    )


if __name__ == "__main__":
    # Test calculations
    calc = InvoiceCalculator(vat_rate=0.15)
    
    # Test single item
    item_result = calc.calculate_item(6087, 1, 0)
    print(f"Item calculation: {item_result}")
    # Expected: total=6087, discount=0, tax=913.05, net=7000.05
    
    # Test invoice
    items = [
        {'item_name': 'مطبخ المنيوم', 'unit_price': 6087, 'quantity': 1, 'discount_percent': 0}
    ]
    invoice_result = calc.calculate_invoice(items, 0)
    print(f"Invoice calculation: {invoice_result}")
    
    # Test formatting
    print(f"Formatted: {format_saudi_number(7000.05)}")
