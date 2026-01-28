"""
Invoice Application - Main Entry Point
نظام الفواتير - نقطة الدخول الرئيسية

A lightweight, offline invoice management system for Saudi Arabia
with VAT support and ZATCA-compliant QR codes.

Usage:
    python main.py

Requirements:
    - Python 3.8+
    - See requirements.txt for dependencies
"""

import sys
import os

# Ensure the application directory is in path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

def check_dependencies():
    """Check if required packages are installed"""
    missing = []
    
    # Check reportlab
    try:
        import reportlab
    except ImportError:
        missing.append('reportlab')
    
    # Check arabic-reshaper
    try:
        import arabic_reshaper
    except ImportError:
        missing.append('arabic-reshaper')
    
    # Check python-bidi
    try:
        from bidi.algorithm import get_display
    except ImportError:
        missing.append('python-bidi')
    
    # Check qrcode
    try:
        import qrcode
    except ImportError:
        missing.append('qrcode')
    
    # Check PIL/Pillow
    try:
        from PIL import Image
    except ImportError:
        missing.append('Pillow')
    
    return missing


def show_dependency_error(missing: list):
    """Show error message for missing dependencies"""
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    
    msg = "المكتبات التالية غير مثبتة:\n"
    msg += "The following packages are not installed:\n\n"
    msg += "\n".join(f"  • {pkg}" for pkg in missing)
    msg += "\n\n"
    msg += "يرجى تثبيتها باستخدام الأمر:\n"
    msg += "Please install them using:\n\n"
    msg += f"pip install {' '.join(missing)}"
    
    messagebox.showerror("خطأ - Error", msg)
    root.destroy()


def main():
    """Main entry point"""
    # Ensure console output can handle Arabic on Windows terminals
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        
        # Try to show GUI error
        try:
            show_dependency_error(missing)
        except:
            pass
        
        # Continue anyway - some features will be disabled
        print("\nStarting with reduced functionality...\n")
    
    # Create necessary directories
    os.makedirs(os.path.join(APP_DIR, 'data'), exist_ok=True)
    os.makedirs(os.path.join(APP_DIR, 'output'), exist_ok=True)
    os.makedirs(os.path.join(APP_DIR, 'backups'), exist_ok=True)
    os.makedirs(os.path.join(APP_DIR, 'assets', 'fonts'), exist_ok=True)
    os.makedirs(os.path.join(APP_DIR, 'assets', 'images'), exist_ok=True)
    
    # Start application
    try:
        from ui.main_window import MainWindow
        
        print("=" * 50)
        print("  Invoice System")
        print("  Version 1.0.0")
        print("=" * 50)
        print()
        
        app = MainWindow()
        app.run()
        
    except Exception as e:
        import traceback
        print(f"Error starting application: {e}")
        traceback.print_exc()
        
        # Show error dialog
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تشغيل البرنامج:\n{str(e)}")
            root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
