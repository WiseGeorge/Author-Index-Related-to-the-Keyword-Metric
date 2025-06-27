import customtkinter as ctk
from tkinter import ttk
from app.gui.styles import PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR
from app.gui.upload_section import UploadSection
from app.gui.data_table import DataTable
from app.gui.authors_list import AuthorsList
from app.gui.wordcloud_viewer import WordCloudViewer
from app.gui.author_keyword_index import AuthorKeywordIndexFrame
import pandas as pd
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainWindow:
    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("Author Index Related to the Keyword (k) Calculator")
        self.root.iconbitmap(resource_path("resources/AIH.ico"))
        
        self.root.geometry("1050x750")
        self.root.resizable(False, False)

        menu_frame = ctk.CTkFrame(self.root, fg_color=BACKGROUND_COLOR)
        menu_frame.pack(fill='x', pady=(0, 5))
        upload_btn = ctk.CTkButton(menu_frame, text="Upload New Author Data", command=self.open_upload_window, fg_color=PRIMARY_COLOR)
        upload_btn.pack(side='left', padx=10, pady=5)
        exit_btn = ctk.CTkButton(menu_frame, text="Exit", command=self.root.quit, fg_color=PRIMARY_COLOR)
        exit_btn.pack(side='left', padx=10, pady=5)
        # About button
        about_btn = ctk.CTkButton(menu_frame, text="About", command=self.show_about_popup, fg_color=PRIMARY_COLOR)
        about_btn.pack(side='right', padx=10, pady=5)
        # Title
        title = ctk.CTkLabel(self.root, text="Author Index Related to the Keyword (k) Calculator", font=("Segoe UI", 16, "bold"), text_color=PRIMARY_COLOR)
        legend1 = ctk.CTkLabel(self.root, text="AIa: Author Index Absolute     -     AIr: Author Index Relative", font=("Segoe UI", 8, "bold"), text_color=PRIMARY_COLOR)

        title.pack(pady=(5, 5))
        legend1.pack(pady=(2, 2))
    
        # --- Año selector frame ---
        year_frame = ctk.CTkFrame(self.root, fg_color=BACKGROUND_COLOR)
        year_frame.pack(fill='x', padx=20, pady=(0, 5))
        year_label = ctk.CTkLabel(year_frame, text="Publication Year Range:", font=("Segoe UI", 11), text_color=PRIMARY_COLOR)
        year_label.pack(side='left', padx=(5, 5))
        # Obtener años disponibles
        from app.logic.file_loader import load_all_data
        df_all = load_all_data()
        if not df_all.empty and 'Publication Year' in df_all.columns:
            years = sorted(df_all['Publication Year'].dropna().unique())
            years = [int(y) for y in years if str(y).isdigit()]
            if not years:
                years = [2022, 2023, 2024]
        else:
            years = [2022, 2023, 2024]
        min_year, max_year = min(years), max(years)
        self.year_start_var = ctk.StringVar(value="2022")
        self.year_end_var = ctk.StringVar(value="2024")
        self.year_start_combo = ctk.CTkComboBox(year_frame, values=[str(y) for y in years], variable=self.year_start_var, width=80, command=self.on_year_change)
        self.year_start_combo.pack(side='left', padx=(5, 2))
        dash_label = ctk.CTkLabel(year_frame, text="-", font=("Segoe UI", 11, "bold"), text_color=PRIMARY_COLOR)
        dash_label.pack(side='left')
        self.year_end_combo = ctk.CTkComboBox(year_frame, values=[str(y) for y in years], variable=self.year_end_var, width=80, command=self.on_year_change)
        self.year_end_combo.pack(side='left', padx=(2, 5))

        # Main vertical frame
        main_frame = ctk.CTkFrame(self.root, fg_color=BACKGROUND_COLOR)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        # Authors list
        self.authors_list = AuthorsList(main_frame)
        self.authors_list.pack(pady=5, fill='x')
        self.authors_list.listbox.bind('<<ListboxSelect>>', self.on_author_select)
        # Publications table
        self.data_table = DataTable(main_frame)
        self.data_table.pack(pady=5, fill='x')
        # Bottom frame: wordcloud and metrics
        bottom_frame = ctk.CTkFrame(main_frame, fg_color=BACKGROUND_COLOR)
        bottom_frame.pack(fill='both', expand=True, pady=(10, 0))
        # WordCloud
        wordcloud_section = ctk.CTkFrame(bottom_frame, fg_color=BACKGROUND_COLOR, border_width=2, border_color=PRIMARY_COLOR)
        wordcloud_section.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.wordcloud_viewer = WordCloudViewer(wordcloud_section)
        self.wordcloud_viewer.pack(fill='both', expand=True)
        # Índices autor/keyword
        index_section = ctk.CTkFrame(bottom_frame, fg_color=BACKGROUND_COLOR, border_width=2, border_color=PRIMARY_COLOR)
        index_section.pack(side='left', fill='both', expand=True)
        self.author_keyword_index = AuthorKeywordIndexFrame(index_section)
        self.author_keyword_index.pack(fill='both', expand=True)
        # Connect index analysis author change to wordcloud update
        self.author_keyword_index.author_combo.configure(command=self.on_index_author_change)
        # Upload window (hidden by default)
        self.upload_window = None

        # Inicializar datos filtrados
        self.update_filtered_data()
    def open_upload_window(self):
        if self.upload_window and ctk.CTkToplevel.winfo_exists(self.upload_window):
            self.upload_window.lift()
            return
        self.upload_window = UploadSection(self.root, data_table=self.data_table, authors_list=self.authors_list)
    def on_author_select(self, event):
        selection = event.widget.curselection()
        if selection:
            author = event.widget.get(selection[0])
            self.wordcloud_viewer.show_for_author(author)
    def on_index_author_change(self, author):
        # Update the wordcloud to reflect the author selected for index analysis
        self.wordcloud_viewer.show_for_author(author)
    def show_about_popup(self):
        popup = ctk.CTkToplevel(self.root)
        popup.title("About")
        popup.geometry("480x220")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_force()
        about_text = (
            "Builded by:\n" 
            "Jorge Felix Martinez Pazos & Jorge Gulin Gonzales\n"
            "Study Center on Computational Mathematics\n"
            "University of Informatics Science, Havana, Cuba"
        )
        label = ctk.CTkLabel(popup, text=about_text, font=("Segoe UI", 13), text_color=PRIMARY_COLOR, justify="center")
        label.pack(pady=30, padx=20)
        close_btn = ctk.CTkButton(popup, text="Exit", command=popup.destroy, fg_color=PRIMARY_COLOR, width=100)
        close_btn.pack(pady=10)
    def run(self):
        self.root.mainloop()

    def get_filtered_df(self):
        from app.logic.file_loader import load_all_data
        df = load_all_data()
        try:
            year_start = int(self.year_start_var.get())
            year_end = int(self.year_end_var.get())
        except Exception:
            year_start, year_end = 2022, 2024
        if not df.empty and 'Publication Year' in df.columns:
            df = df[df['Publication Year'].apply(lambda y: str(y).isdigit() and year_start <= int(y) <= year_end)]
        return df

    def update_filtered_data(self):
        df = self.get_filtered_df()
        if hasattr(self.authors_list, 'set_data'):
            self.authors_list.set_data(df)
        else:
            self.authors_list.refresh()
        if hasattr(self.data_table, 'set_data'):
            self.data_table.set_data(df)
        else:
            self.data_table.refresh()
        if hasattr(self.author_keyword_index, 'set_data'):
            self.author_keyword_index.set_data(df)
        else:
            self.author_keyword_index.df = df
            self.author_keyword_index.refresh_authors()

    def on_year_change(self, *args):
        self.update_filtered_data() 