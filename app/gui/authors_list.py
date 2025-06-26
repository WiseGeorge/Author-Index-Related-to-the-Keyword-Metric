import customtkinter as ctk
from app.gui.styles import BACKGROUND_COLOR, PRIMARY_COLOR
from app.logic.file_loader import load_all_data
import tkinter as tk

class AuthorsList(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BACKGROUND_COLOR)
        label = ctk.CTkLabel(self, text="Authors List:", font=("Segoe UI", 12, "bold"), text_color=PRIMARY_COLOR)
        label.pack(anchor='w', padx=10)
        self.listbox = tk.Listbox(self, height=5, font=("Segoe UI", 10))
        self.listbox.pack(fill='x', padx=10)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        df = load_all_data()
        if not df.empty and '__author__' in df.columns:
            authors = sorted(df['__author__'].unique())
            for author in authors:
                self.listbox.insert('end', author)

    # Placeholder de autores
    #self.listbox.insert('end', "Ejemplo Autor") 