"""
Invoice Application - QR Code Generator
Generates ZATCA-compliant QR codes for Saudi e-invoicing
"""

from __future__ import annotations

import base64
from io import BytesIO
from typing import Optional, TYPE_CHECKING, Any
from datetime import datetime

try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    Image = None  # type: ignore
    print("Warning: qrcode or Pillow not installed. QR codes will not be generated.")


class ZATCAQRGenerator:
    """
    Generates ZATCA (Zakat, Tax and Customs Authority) compliant QR codes
    Using TLV (Tag-Length-Value) encoding format
    
    Tags:
    1 - Seller Name (UTF-8)
    2 - VAT Registration Number
    3 - Timestamp (ISO 8601 format)
    4 - Invoice Total (with VAT)
    5 - VAT Amount
    """
    
    @staticmethod
    def encode_tlv(tag: int, value: str) -> bytes:
        """
        Encode a single TLV field
        
        Args:
            tag: Tag number (1-5)
            value: Value to encode
            
        Returns:
            Encoded bytes in TLV format
        """
        value_bytes = value.encode('utf-8')
        length = len(value_bytes)
        return bytes([tag, length]) + value_bytes
    
    @staticmethod
    def generate_qr_data(
        seller_name: str,
        vat_number: str,
        timestamp: str,
        total_with_vat: float,
        vat_amount: float
    ) -> str:
        """
        Generate Base64 encoded TLV data for QR code
        
        Args:
            seller_name: Company/seller name (Arabic)
            vat_number: VAT registration number
            timestamp: Invoice timestamp (ISO 8601)
            total_with_vat: Total amount including VAT
            vat_amount: VAT amount
            
        Returns:
            Base64 encoded string for QR code
        """
        # Build TLV data
        tlv_data = b''
        tlv_data += ZATCAQRGenerator.encode_tlv(1, seller_name)
        tlv_data += ZATCAQRGenerator.encode_tlv(2, vat_number)
        tlv_data += ZATCAQRGenerator.encode_tlv(3, timestamp)
        tlv_data += ZATCAQRGenerator.encode_tlv(4, f"{total_with_vat:.2f}")
        tlv_data += ZATCAQRGenerator.encode_tlv(5, f"{vat_amount:.2f}")
        
        # Encode to Base64
        return base64.b64encode(tlv_data).decode('utf-8')
    
    @staticmethod
    def generate_qr_image(
        seller_name: str,
        vat_number: str,
        timestamp: str = None,
        total_with_vat: float = 0.0,
        vat_amount: float = 0.0,
        size: int = 200,
        border: int = 2
    ) -> Optional[Any]:
        """
        Generate QR code image
        
        Args:
            seller_name: Company/seller name
            vat_number: VAT registration number
            timestamp: Invoice timestamp (defaults to now)
            total_with_vat: Total amount including VAT
            vat_amount: VAT amount
            size: Image size in pixels
            border: QR code border width
            
        Returns:
            PIL Image object or None if qrcode not available
        """
        if not QR_AVAILABLE:
            return None
        
        # Use current timestamp if not provided
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Generate QR data
        qr_data = ZATCAQRGenerator.generate_qr_data(
            seller_name, vat_number, timestamp, total_with_vat, vat_amount
        )
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=border
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize to desired size
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        return img
    
    @staticmethod
    def save_qr_image(
        filepath: str,
        seller_name: str,
        vat_number: str,
        timestamp: str = None,
        total_with_vat: float = 0.0,
        vat_amount: float = 0.0,
        size: int = 200
    ) -> bool:
        """
        Generate and save QR code image to file
        
        Args:
            filepath: Path to save the image
            (other args same as generate_qr_image)
            
        Returns:
            True if successful, False otherwise
        """
        img = ZATCAQRGenerator.generate_qr_image(
            seller_name, vat_number, timestamp, 
            total_with_vat, vat_amount, size
        )
        
        if img:
            try:
                img.save(filepath)
                return True
            except Exception as e:
                print(f"Error saving QR image: {e}")
        
        return False
    
    @staticmethod
    def get_qr_bytes(
        seller_name: str,
        vat_number: str,
        timestamp: str = None,
        total_with_vat: float = 0.0,
        vat_amount: float = 0.0,
        size: int = 200
    ) -> Optional[bytes]:
        """
        Generate QR code and return as bytes (for embedding in PDF)
        
        Returns:
            PNG image bytes or None
        """
        img = ZATCAQRGenerator.generate_qr_image(
            seller_name, vat_number, timestamp,
            total_with_vat, vat_amount, size
        )
        
        if img:
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()
        
        return None
    
    @staticmethod
    def decode_qr_data(base64_data: str) -> dict:
        """
        Decode ZATCA QR code data (for verification)
        
        Args:
            base64_data: Base64 encoded TLV string
            
        Returns:
            Dictionary with decoded values
        """
        try:
            data = base64.b64decode(base64_data)
            result = {}
            tag_names = {
                1: 'seller_name',
                2: 'vat_number',
                3: 'timestamp',
                4: 'total_with_vat',
                5: 'vat_amount'
            }
            
            pos = 0
            while pos < len(data):
                tag = data[pos]
                length = data[pos + 1]
                value = data[pos + 2:pos + 2 + length].decode('utf-8')
                
                if tag in tag_names:
                    result[tag_names[tag]] = value
                
                pos += 2 + length
            
            return result
        except Exception as e:
            print(f"Error decoding QR data: {e}")
            return {}


def generate_invoice_qr(invoice_data: dict, company_settings: dict) -> Optional[bytes]:
    """
    Convenience function to generate QR code for an invoice
    
    Args:
        invoice_data: Invoice dictionary with net_total, tax_amount, invoice_date
        company_settings: Company settings with company_name_ar, tax_number
        
    Returns:
        PNG image bytes
    """
    timestamp = f"{invoice_data.get('invoice_date', '')}T{invoice_data.get('invoice_time', '00:00:00')}Z"
    
    return ZATCAQRGenerator.get_qr_bytes(
        seller_name=company_settings.get('company_name_ar', ''),
        vat_number=company_settings.get('tax_number', ''),
        timestamp=timestamp,
        total_with_vat=invoice_data.get('net_total', 0),
        vat_amount=invoice_data.get('tax_amount', 0)
    )


if __name__ == "__main__":
    # Test QR generation
    print("Testing ZATCA QR Generator...")
    
    # Generate test QR data
    qr_data = ZATCAQRGenerator.generate_qr_data(
        seller_name="مؤسسة التفرد الاصيل للمطابخ",
        vat_number="300694858900003",
        timestamp="2025-03-06T05:37:56Z",
        total_with_vat=7000.05,
        vat_amount=913.05
    )
    print(f"QR Data (Base64): {qr_data[:50]}...")
    
    # Decode to verify
    decoded = ZATCAQRGenerator.decode_qr_data(qr_data)
    print(f"Decoded: {decoded}")
    
    # Generate image
    if QR_AVAILABLE:
        img = ZATCAQRGenerator.generate_qr_image(
            seller_name="مؤسسة التفرد الاصيل للمطابخ",
            vat_number="300694858900003",
            total_with_vat=7000.05,
            vat_amount=913.05
        )
        if img:
            print(f"QR Image generated: {img.size}")
    else:
        print("QR code libraries not installed")
