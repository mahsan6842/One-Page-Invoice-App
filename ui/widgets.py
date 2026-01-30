"""
Invoice Application - Custom Widgets
Reusable Tkinter widgets with Arabic support
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional, Any

from app.i18n import get_current_lang, is_rtl, LANG_AR, t, anchor_for, justify_for, pack_side, pack_side_opposite, tree_anchor_for


def bind_canvas_resize(canvas: tk.Canvas, window_id: int) -> None:
    """Bind canvas Configure to update inner frame width for responsive behavior."""
    def _on_configure(event):
        canvas.itemconfig(window_id, width=event.width)
    canvas.bind('<Configure>', _on_configure)


def apply_direction_recursive(widget: tk.Widget, lang: str) -> None:
    """Recursively apply direction to widget and its descendants that support it."""
    if hasattr(widget, 'apply_direction'):
        widget.apply_direction(lang)
    try:
        for child in widget.winfo_children():
            apply_direction_recursive(child, lang)
    except tk.TclError:
        pass


class ArabicEntry(ttk.Entry):
    """Entry widget with RTL support for Arabic text"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.apply_direction(get_current_lang() or LANG_AR)
    
    def apply_direction(self, lang: str):
        """Update text alignment based on language direction."""
        self.configure(justify=justify_for(lang))


class ArabicLabel(ttk.Label):
    """Label with RTL support"""
    
    def __init__(self, parent, **kwargs):
        self._direction_controlled = 'anchor' not in kwargs
        if self._direction_controlled:
            kwargs['anchor'] = anchor_for(get_current_lang() or LANG_AR)
        super().__init__(parent, **kwargs)
    
    def apply_direction(self, lang: str):
        """Update alignment based on language direction."""
        if self._direction_controlled:
            self.configure(anchor=anchor_for(lang))


class NumberEntry(ttk.Entry):
    """Entry that only accepts numbers"""
    
    def __init__(self, parent, allow_decimal: bool = True, 
                 allow_negative: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.allow_decimal = allow_decimal
        self.allow_negative = allow_negative
        
        # Register validation
        vcmd = (self.register(self._validate), '%P')
        self.configure(validate='key', validatecommand=vcmd)
        self.apply_direction(get_current_lang() or LANG_AR)
    
    def apply_direction(self, lang: str):
        """Update text alignment based on language direction."""
        self.configure(justify=justify_for(lang))
    
    def _validate(self, value: str) -> bool:
        if value == '' or value == '-':
            return True
        
        try:
            if self.allow_decimal:
                float(value)
            else:
                int(value)
            
            if not self.allow_negative and value.startswith('-'):
                return False
            
            return True
        except ValueError:
            return False
    
    def get_value(self) -> float:
        """Get numeric value"""
        try:
            return float(self.get())
        except ValueError:
            return 0.0


class LabeledEntry(ttk.Frame):
    """Entry with label above it"""
    
    def __init__(self, parent, label_text: str, entry_type: str = 'text', 
                 width: int = 20, **kwargs):
        super().__init__(parent)
        lang = get_current_lang() or LANG_AR
        self.label = ArabicLabel(self, text=label_text)
        self.label.pack(anchor=anchor_for(lang), pady=(0, 2))
        
        # Entry
        if entry_type == 'number':
            self.entry = NumberEntry(self, width=width, **kwargs)
        else:
            self.entry = ArabicEntry(self, width=width)
        self.entry.pack(fill='x')
    
    def get(self) -> str:
        return self.entry.get()
    
    def set(self, value: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
    
    def get_value(self) -> float:
        if isinstance(self.entry, NumberEntry):
            return self.entry.get_value()
        try:
            return float(self.entry.get())
        except ValueError:
            return 0.0

    def apply_direction(self, lang: str):
        """Update label anchor based on language direction."""
        self.label.pack_forget()
        self.label.pack(anchor=anchor_for(lang), pady=(0, 2))


class AutocompleteEntry(ttk.Entry):
    """Entry with autocomplete dropdown"""
    
    def __init__(self, parent, values: List[str] = None, 
                 on_select: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.values = values or []
        self.on_select = on_select
        self.listbox = None
        self.listbox_window = None
        
        # Bindings
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusOut>', self._hide_listbox)
        self.bind('<Return>', self._on_select)
        self.bind('<Down>', self._move_down)
        self.bind('<Up>', self._move_up)
    
    def set_values(self, values: List[str]):
        """Update autocomplete values"""
        self.values = values
    
    def _on_key_release(self, event):
        if event.keysym in ('Down', 'Up', 'Return', 'Escape'):
            return
        
        text = self.get()
        if len(text) < 1:
            self._hide_listbox()
            return
        
        # Filter values
        matches = [v for v in self.values if text.lower() in v.lower()]
        
        if matches:
            self._show_listbox(matches)
        else:
            self._hide_listbox()
    
    def _show_listbox(self, values: List[str]):
        if self.listbox_window:
            self.listbox_window.destroy()
        
        # Create popup window
        self.listbox_window = tk.Toplevel(self)
        self.listbox_window.wm_overrideredirect(True)
        
        # Position below entry
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.listbox_window.geometry(f"+{x}+{y}")
        
        # Create listbox
        self.listbox = tk.Listbox(self.listbox_window, height=min(5, len(values)))
        self.listbox.pack(fill='both', expand=True)
        
        for value in values[:10]:  # Limit to 10 items
            self.listbox.insert(tk.END, value)
        
        self.listbox.bind('<ButtonRelease-1>', self._on_select)
        self.listbox.bind('<Return>', self._on_select)
    
    def _hide_listbox(self, event=None):
        if self.listbox_window:
            self.listbox_window.destroy()
            self.listbox_window = None
            self.listbox = None
    
    def _on_select(self, event=None):
        if self.listbox and self.listbox.curselection():
            value = self.listbox.get(self.listbox.curselection())
            self.delete(0, tk.END)
            self.insert(0, value)
            if self.on_select:
                self.on_select(value)
        self._hide_listbox()
    
    def _move_down(self, event):
        if self.listbox:
            idx = self.listbox.curselection()
            if idx:
                new_idx = min(idx[0] + 1, self.listbox.size() - 1)
            else:
                new_idx = 0
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(new_idx)
    
    def _move_up(self, event):
        if self.listbox:
            idx = self.listbox.curselection()
            if idx:
                new_idx = max(idx[0] - 1, 0)
            else:
                new_idx = 0
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(new_idx)


class ScrollableFrame(ttk.Frame):
    """Frame with scrollbar support"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(self, highlightthickness=0)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', 
                                       command=self.canvas.yview)
        
        # Inner frame
        self.inner_frame = ttk.Frame(self.canvas)
        
        # Window in canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.inner_frame, anchor='nw'
        )
        
        # Configure
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        lang = get_current_lang() or LANG_AR
        ps, pso = pack_side(lang), pack_side_opposite(lang)
        self.scrollbar.pack(side=pso, fill='y')
        self.canvas.pack(side=ps, fill='both', expand=True)
        
        # Bindings
        self.inner_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Mouse wheel
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)

    def apply_direction(self, lang: str):
        """Repack scrollbar and canvas for language direction."""
        ps, pso = pack_side(lang), pack_side_opposite(lang)
        self.scrollbar.pack_forget()
        self.canvas.pack_forget()
        self.scrollbar.pack(side=pso, fill='y')
        self.canvas.pack(side=ps, fill='both', expand=True)
    
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')


class DataTable(ttk.Frame):
    """Simple data table widget"""
    
    def __init__(self, parent, columns: List[tuple], **kwargs):
        """
        Args:
            columns: List of (column_id, header_text, width) tuples
        """
        super().__init__(parent, **kwargs)
        
        self.columns = columns
        self.rows = []
        self.on_select = None
        self.on_double_click = None
        
        # Create Treeview
        col_ids = [c[0] for c in columns]
        self.tree = ttk.Treeview(self, columns=col_ids, show='headings',
                     selectmode='browse', style='App.Treeview')
        
        lang = get_current_lang() or LANG_AR
        ta = tree_anchor_for(lang)
        ps, pso = pack_side(lang), pack_side_opposite(lang)
        for col_id, header, width in columns:
            self.tree.heading(col_id, text=header, anchor=ta)
            self.tree.column(col_id, width=width, anchor=ta)
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.pack(side=ps, fill='both', expand=True)
        self.scrollbar.pack(side=pso, fill='y')
        
        # Bindings
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)

    def apply_direction(self, lang: str):
        """Update tree anchors and repack for language direction."""
        ta = tree_anchor_for(lang)
        ps, pso = pack_side(lang), pack_side_opposite(lang)
        for col_id, header, width in self.columns:
            self.tree.heading(col_id, anchor=ta)
            self.tree.column(col_id, anchor=ta)
        self.tree.pack_forget()
        self.scrollbar.pack_forget()
        self.tree.pack(side=ps, fill='both', expand=True)
        self.scrollbar.pack(side=pso, fill='y')
    
    def set_data(self, data: List[List[Any]]):
        """Set table data"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.rows = data
        
        # Insert rows
        for row in data:
            values = [row.get(c[0], '') for c in self.columns]
            self.tree.insert('', tk.END, values=values, tags=(row.get('id', ''),))
    
    def get_selected(self) -> Optional[dict]:
        """Get selected row data"""
        selection = self.tree.selection()
        if selection:
            idx = self.tree.index(selection[0])
            if idx < len(self.rows):
                return self.rows[idx]
        return None
    
    def _on_select(self, event):
        if self.on_select:
            self.on_select(self.get_selected())
    
    def _on_double_click(self, event):
        if self.on_double_click:
            self.on_double_click(self.get_selected())


class StatusBar(ttk.Frame):
    """Status bar for bottom of window"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        lang = get_current_lang() or LANG_AR
        self.label = ttk.Label(self, text=t("common.ready", lang), anchor=anchor_for(lang),
                       style='Status.TLabel')
        self.label.pack(fill='x', padx=5, pady=2)
    
    def set_status(self, text: str):
        self.label.configure(text=text)
    
    def set_success(self, text: str):
        self.label.configure(text=f"✓ {text}")
    
    def set_error(self, text: str):
        self.label.configure(text=f"✗ {text}")

    def apply_language(self):
        """Update alignment based on current language direction."""
        lang = get_current_lang() or LANG_AR
        self.label.configure(anchor=anchor_for(lang))


class ToolButton(ttk.Button):
    """Styled toolbar button"""
    
    def __init__(self, parent, text: str, command: Callable = None, **kwargs):
        super().__init__(parent, text=text, command=command, style='Toolbar.TButton', **kwargs)
        self.configure(width=12)


class FormSection(ttk.LabelFrame):
    """Styled section frame for forms"""
    
    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, text=title, style='Section.TLabelframe', **kwargs)
        self.configure(padding=10)
