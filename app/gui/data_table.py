import customtkinter as ctk
from tkinter import ttk
from app.gui.styles import TABLE_HEADER_BG, TABLE_ROW_BG, TABLE_ROW_ALT_BG, TEXT_COLOR, BACKGROUND_COLOR
from app.logic.file_loader import load_all_data

class DataTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BACKGROUND_COLOR)
        # Optionally, add a label for the table
        table_label = ctk.CTkLabel(self, text="Publications", font=("Segoe UI", 12, "bold"), text_color=TEXT_COLOR)
        table_label.pack(anchor='w', padx=10, pady=(0, 2))
        self.columns = ["Authors", "Article Title", "Publication Year", "Times Cited"]
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings', height=8)
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor='center')
        self.tree.pack(fill='x')
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        df = load_all_data()
        if not df.empty:
            for _, row in df.iterrows():
                self.tree.insert('', 'end', values=(
                    row.get('Authors', ''),
                    row.get('Article Title', ''),
                    row.get('Publication Year', ''),
                    row.get('Times Cited, WoS Core', row.get('Times Cited', ''))
                ))

    def set_data(self, df):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if not df.empty:
            for _, row in df.iterrows():
                self.tree.insert('', 'end', values=(
                    row.get('Authors', ''),
                    row.get('Article Title', ''),
                    row.get('Publication Year', ''),
                    row.get('Times Cited, WoS Core', row.get('Times Cited', ''))
                )) 