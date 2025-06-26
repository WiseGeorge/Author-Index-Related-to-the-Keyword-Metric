import customtkinter as ctk
from tkinter import filedialog
from app.gui.styles import PRIMARY_COLOR, BACKGROUND_COLOR
from app.logic.file_loader import save_file_for_author

class UploadSection(ctk.CTkToplevel):
    def __init__(self, parent, data_table=None, authors_list=None):
        super().__init__(parent)
        self.title("Upload Author File")
        self.geometry("420x70")
        self.resizable(False, False)
        self.configure(bg=BACKGROUND_COLOR)
        self.data_table = data_table
        self.authors_list = authors_list
        self.label = ctk.CTkLabel(self, text="Author Name:", font=("Segoe UI", 12, "bold"), text_color=PRIMARY_COLOR)
        self.label.pack(side='left', padx=10)
        self.author_entry = ctk.CTkEntry(self, font=("Segoe UI", 10), width=180)
        self.author_entry.pack(side='left', padx=5)
        self.upload_btn = ctk.CTkButton(self, text="Select File", fg_color=PRIMARY_COLOR, command=self.select_file)
        self.upload_btn.pack(side='left', padx=10)
        self.status = ctk.CTkLabel(self, text="", font=("Segoe UI", 10), text_color=PRIMARY_COLOR)
        self.status.pack(side='left', padx=10)
        # Mantener la ventana al frente y enfocada
        self.attributes('-topmost', True)
        self.focus_force()
        self.grab_set()  # Modal
    def select_file(self):
        author = self.author_entry.get().strip()
        if not author:
            self.status.configure(text="Insert Author Name.")
            return
        file_path = filedialog.askopenfilename(filetypes=[("Excel/CSV Files", "*.csv *.xlsx *.xls")])
        if file_path:
            try:
                save_file_for_author(author, file_path)
                self.status.configure(text=f"Upladed File for {author}")
                if self.data_table:
                    self.data_table.refresh()
                if self.authors_list:
                    self.authors_list.refresh()
                # Refresca el frame de índices si está disponible
                if hasattr(self.master, 'author_keyword_index'):
                    self.master.author_keyword_index.refresh_authors()
                self.destroy()  # Cierra la ventana tras éxito
            except Exception as e:
                self.status.configure(text=f"Error: {e}") 