import customtkinter as ctk
from app.gui.styles import BACKGROUND_COLOR, PRIMARY_COLOR, TEXT_COLOR
from app.logic.file_loader import load_all_data, resource_path, get_persistent_data_dir
import pandas as pd
import ast
from tkinter import StringVar
import os
import re
from collections import Counter
import unicodedata
from tkinter import filedialog  # <-- Agregado para el diálogo de guardar

FIXED_WIDTH = 600
FIXED_HEIGHT = 300
MAX_KEYWORDS = 15
AUTHOR_COL = 'Author Full Names'

class AuthorKeywordIndexFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BACKGROUND_COLOR, width=FIXED_WIDTH, height=FIXED_HEIGHT)
        self.pack_propagate(False)
        self.label = ctk.CTkLabel(self, text="Autor/Keyword Indexes", font=("Segoe UI", 12, "bold"), text_color=PRIMARY_COLOR)
        self.label.pack(pady=(5, 0))

        self.df = load_all_data()
        self.folder_authors = self._get_folder_authors()
        self.authors = self._get_authors()
        self.current_keywords = []

        # Row for author, keyword entry, and calculate button side by side
        self.top_row = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.top_row.pack(pady=(10, 0), padx=10, fill="x")
        self.author_var = StringVar()
        self.author_combo = ctk.CTkComboBox(self.top_row, values=self.authors, width=140, command=self.on_author_change, variable=self.author_var)
        self.author_combo.pack(side="left", padx=(0, 10), pady=2)
        if self.authors:
            self.author_combo.set(self.authors[0])
        self.refresh_btn = ctk.CTkButton(self.top_row, text="⟳", width=28, height=28, font=("Segoe UI", 14), command=self.refresh_authors)
        self.refresh_btn.pack(side="left", padx=(0, 6), pady=2)
        self.keyword_var = StringVar()
        self.keyword_entry = ctk.CTkEntry(self.top_row, textvariable=self.keyword_var, width=140)
        self.keyword_entry.pack(side="left", padx=(0, 10), pady=2)
        self.keyword_entry.bind('<KeyRelease>', self.on_keyword_type)
        self.keyword_entry.bind('<Return>', self.on_keyword_enter)
        self.keyword_entry.bind('<FocusOut>', self.on_keyword_focus_out)
        self.keyword_entry.bind('<Escape>', self.on_keyword_escape)
        self.calc_btn = ctk.CTkButton(self.top_row, text="Calculate Indexes", command=self.calculate_indexes, width=120, height=32, font=("Segoe UI", 12, "bold"))
        self.calc_btn.pack(side="left", padx=(0, 10), pady=2)
        # Details button: do not pack initially
        self.details_btn = ctk.CTkButton(self.top_row, text="View details", fg_color=PRIMARY_COLOR, width=120, height=32, font=("Segoe UI", 12, "bold"), command=self._show_last_result_details)
        # self.details_btn.pack(side="left", padx=(0, 0), pady=2)  # Only pack after calculation

        # Dedicated frame for recommended keywords (grid, empty by default)
        self.recommend_frame = ctk.CTkFrame(self, fg_color="#fff", border_width=2, border_color=PRIMARY_COLOR, corner_radius=8, width=410, height=70)
        self.recommend_frame.pack(pady=(8, 0), padx=10, fill="x")
        self.recommend_frame.pack_propagate(False)
        self.recommend_labels = []

        # Result frame below (instead of label)
        self.result_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.result_frame.pack(pady=5, fill="both", expand=True)

        if self.authors:
            self.update_keywords_for_author(self.authors[0])

    def _get_folder_authors(self):
        # Solo autores que tienen carpeta en la carpeta persistente de datos
        base_dir = get_persistent_data_dir()
        if not os.path.exists(base_dir):
            return []
        return sorted([name for name in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, name))])

    def _get_authors(self):
        # Solo autores que están en las carpetas y en los datos
        if self.df.empty or AUTHOR_COL not in self.df.columns:
            return []
        authors = set()
        for val in self.df[AUTHOR_COL].dropna():
            if isinstance(val, str):
                for name in val.split(';'):
                    name = name.strip()
                    if name and name in self.folder_authors:
                        authors.add(name)
        # Si no hay coincidencias exactas, usar los nombres de carpeta
        if not authors:
            return self.folder_authors
        return sorted(authors)

    def update_keywords_for_author(self, author):
        df_author = filter_papers_by_authors(self.df, author)
        self.current_keywords = [slugify_keyword(kw) for kw in get_keywords_for_author(df_author) if isinstance(kw, str) and kw.strip()]
        self.keyword_var.set("")
        self.clear_recommendations()
        self.clear_result()

    def on_author_change(self, author):
        self.update_keywords_for_author(author)

    def on_keyword_type(self, event):
        typed = slugify_keyword(self.keyword_var.get().strip())
        if not typed:
            self.clear_recommendations()
            return
        filtered = [kw for kw in self.current_keywords if typed in kw]
        self.show_recommendations(filtered)

    def on_keyword_enter(self, event):
        self.clear_recommendations()
        self.calculate_indexes()

    def on_keyword_focus_out(self, event):
        self.clear_recommendations()

    def on_keyword_escape(self, event):
        self.clear_recommendations()

    def clear_recommendations(self):
        for lbl in self.recommend_labels:
            lbl.destroy()
        self.recommend_labels = []

    def show_recommendations(self, keywords):
        self.clear_recommendations()
        if not keywords:
            lbl = ctk.CTkLabel(self.recommend_frame, text="No keywords found", text_color=PRIMARY_COLOR, font=("Segoe UI", 10, "italic"), padx=8, pady=4)
            lbl.grid(row=0, column=0, padx=8, pady=2, sticky="w")
            self.recommend_labels.append(lbl)
            return
        # Show in grid, 5 per row, 2 rows max
        for i, kw in enumerate(keywords[:10]):
            row = i // 5
            col = i % 5
            lbl = ctk.CTkLabel(self.recommend_frame, text=kw, text_color=PRIMARY_COLOR, cursor="hand2", font=("Segoe UI", 10, "italic"), padx=8, pady=2)
            lbl.grid(row=row, column=col, padx=8, pady=2, sticky="w")
            lbl.bind('<Button-1>', lambda e, k=kw: self.on_keyword_select(k))
            self.recommend_labels.append(lbl)

    def on_keyword_select(self, keyword):
        self.keyword_var.set(keyword)
        self.clear_recommendations()
        self.calculate_indexes()

    def clear_result(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

    def calculate_indexes(self):
        # Hide details button before calculation
        if self.details_btn.winfo_ismapped():
            self.details_btn.pack_forget()
        author = self.author_combo.get()
        keyword = self.keyword_var.get().strip()
        if not author or not keyword:
            self.show_result_message("Select Author & Keyword")
            return
        # Validar si la keyword está en las del autor
        if keyword.lower() not in [k.lower() for k in self.current_keywords]:
            self.show_result_message("The keyword is not present in this author's publications.")
            return
        try:
            result = calculate_indexes_by_author(self.df, author, '', keyword)
            self.show_metric_result(result)
        except Exception as e:
            self.show_result_message(f"Error en el cálculo: {e}")

    def show_result_message(self, msg):
        # Clear previous result widgets
        self.clear_result()
        # Show message
        msg_label = ctk.CTkLabel(self.result_frame, text=msg, font=("Segoe UI", 10), text_color=PRIMARY_COLOR)
        msg_label.pack(pady=20)

    def show_metric_result(self, result):
        self.clear_result()
        self._last_result = result
        # Show details button after successful calculation
        if not self.details_btn.winfo_ismapped():
            self.details_btn.pack(side="left", padx=(0, 0), pady=2)
        # Keyword title
        kw_label = ctk.CTkLabel(self.result_frame, text=f"Keyword: {result['keyword'].replace('_', ' ').title()}", font=("Segoe UI", 14, "bold"), text_color=PRIMARY_COLOR)
        kw_label.pack(pady=(5, 10))
        # Metrics row (centered)
        metrics_row = ctk.CTkFrame(self.result_frame, fg_color=BACKGROUND_COLOR)
        metrics_row.pack(pady=(0, 4), padx=10)  # Menor separación para el botón Export
        metrics_row.grid_columnconfigure(0, weight=1)
        metrics_row.grid_columnconfigure(1, weight=1)
        blue1 = PRIMARY_COLOR  # main blue
        blue2 = '#64b5f6'      # lighter blue
        colors = [blue1, blue2]
        for idx, (label, value) in enumerate([
            ("AIa", round(result["I1"],1)),
            ("AIr", round(result["I2"],1))
        ]):
            color = colors[idx]
            metric_canvas = ctk.CTkCanvas(metrics_row, width=75, height=75, bg=BACKGROUND_COLOR, highlightthickness=0)
            metric_canvas.grid(row=0, column=idx, padx=30)
            metric_canvas.create_oval(5, 5, 70, 70, fill=color, outline="")
            metric_canvas.create_text(37, 32, text=str(value), font=("Segoe UI", 14, "bold"), fill="white")
            metric_canvas.create_text(37, 60, text=label, font=("Segoe UI", 9, "bold"), fill="white")
        # Botón Export debajo de los círculos
        export_btn = ctk.CTkButton(self.result_frame, text="Export", width=60, height=28, font=("Segoe UI", 10), command=self.export_indexes_to_excel)
        export_btn.pack(pady=(0, 10))

    def show_result_table_popup(self, result):
        popup = ctk.CTkToplevel(self)
        popup.title("Indexes Details")
        popup.geometry("440x360")
        popup.resizable(False, False)
        # Make popup modal and focused
        popup.grab_set()
        popup.focus_force()
        # Scrollable frame for the table
        try:
            from customtkinter import CTkScrollableFrame
        except ImportError:
            from customtkinter import CTkFrame as CTkScrollableFrame  # fallback
        scroll_frame = CTkScrollableFrame(popup, fg_color="#fff", border_width=1, border_color=PRIMARY_COLOR, corner_radius=8, width=250, height=200)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        # Prepare data for table (omit author, author_class, keyword, I1, I2)
        table_fields = [
            ("KPI Top 3 Positional Avg", result["kpi_t3_positional_avg"]),
            ("KPI Top 3 Citation Avg", result["kpi_t3_citation_avg"]),
            ("KPI Total Positional Avg", result["kpi_total_positional_avg"]),
            ("KPI Total Citation Avg", result["kpi_total_citation_avg"]),
            ("Total Citations", result["total_citations"]),
            ("Total Citations (Keyword)", result["total_citations_k"]),
            ("Total Articles", result["total_articles"]),
            ("Total Articles (Keyword)", result["total_articles_k"]),
        ]
        # Table header
        for col, (header, _) in enumerate([("Metric", None), ("Value", None)]):
            lbl = ctk.CTkLabel(scroll_frame, text=header, font=("Segoe UI", 11, "bold"), text_color=PRIMARY_COLOR, fg_color="#e3eaf2", corner_radius=4)
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1, ipadx=4, ipady=2)
        # Table rows
        for i, (label, value) in enumerate(table_fields):
            bg = "#f5f5f5" if i % 2 == 0 else "#e3eaf2"
            lbl1 = ctk.CTkLabel(scroll_frame, text=label, font=("Segoe UI", 10), text_color=PRIMARY_COLOR, fg_color=bg, anchor="w")
            lbl1.grid(row=i+1, column=0, sticky="nsew", padx=1, pady=1, ipadx=4, ipady=2)
            lbl2 = ctk.CTkLabel(scroll_frame, text=str(value), font=("Segoe UI", 10, "bold"), text_color=TEXT_COLOR, fg_color=bg, anchor="e")
            lbl2.grid(row=i+1, column=1, sticky="nsew", padx=1, pady=1, ipadx=4, ipady=2)
        # Make columns expand
        scroll_frame.grid_columnconfigure(0, weight=2)
        scroll_frame.grid_columnconfigure(1, weight=1)

    def _show_last_result_details(self):
        if hasattr(self, '_last_result') and self._last_result:
            self.show_result_table_popup(self._last_result)

    def get_selected_author(self):
        """Return the currently selected author in the index analysis combobox."""
        return self.author_combo.get()

    def refresh_authors(self):
        """Recarga la lista de autores y actualiza el combobox."""
        self.df = load_all_data()
        self.folder_authors = self._get_folder_authors()
        self.authors = self._get_authors()
        self.author_combo.configure(values=self.authors)
        if self.authors:
            self.author_combo.set(self.authors[0])
            self.update_keywords_for_author(self.authors[0])
        else:
            self.author_var.set("")
            self.current_keywords = []
            self.clear_recommendations()
            self.clear_result()

    def export_indexes_to_excel(self):
        """Exporta los índices calculados y detalles a un archivo Excel."""
        if not hasattr(self, '_last_result') or not self._last_result:
            return
        result = self._last_result
        # Preparar los datos para exportar
        export_data = {
            'Author': [result['author']],
            'Keyword': [result['keyword']],
            'AIa': [result['I1']],
            'AIr': [result['I2']],
            'KPI Top 3 Positional Avg': [result['kpi_t3_positional_avg']],
            'KPI Top 3 Citation Avg': [result['kpi_t3_citation_avg']],
            'KPI Total Positional Avg': [result['kpi_total_positional_avg']],
            'KPI Total Citation Avg': [result['kpi_total_citation_avg']],
            'Total Citations': [result['total_citations']],
            'Total Citations (Keyword)': [result['total_citations_k']],
            'Total Articles': [result['total_articles']],
            'Total Articles (Keyword)': [result['total_articles_k']],
        }
        df_export = pd.DataFrame(export_data)
        # Diálogo para guardar archivo
        file_path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel Files', '*.xlsx')],
            title='Export Indexes to Excel'
        )
        if file_path:
            try:
                df_export.to_excel(file_path, index=False)
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Export Error", f"Could not export to Excel:\n{e}")

    def set_data(self, df):
        self.df = df
        self.folder_authors = self._get_folder_authors()
        self.authors = self._get_authors()
        self.author_combo.configure(values=self.authors)
        if self.authors:
            self.author_combo.set(self.authors[0])
            self.update_keywords_for_author(self.authors[0])
        else:
            self.keyword_var.set("")
            self.clear_recommendations()
            self.clear_result()

# --- Lógica de cálculo adaptada y helpers ---
def calculate_indexes_by_author(df, author_name, author_class, keyword):
    author_papers_df = filter_papers_by_authors(df, author_name)
    author_papers_df = add_author_position_with_score(author_papers_df, author_name)
    keywords_df = filter_articles_by_keyword(author_papers_df, keyword)
    top3_keywords_df = keywords_df.sort_values(by='Times Cited, All Databases', ascending=False).head(3)
    author_t3_position_avg = top3_keywords_df['author_position_score'].mean()
    author_t3_citation_avg = top3_keywords_df['Times Cited, All Databases'].mean()
    author_total_position_avg = keywords_df['author_position_score'].mean()
    author_total_citation_avg = keywords_df['Times Cited, All Databases'].mean()
    total_citations = author_papers_df['Times Cited, All Databases'].sum()
    total_citations_k = keywords_df['Times Cited, All Databases'].sum()
    I1 = author_t3_citation_avg * author_t3_position_avg if author_t3_citation_avg and author_t3_position_avg else 0
    I2 = I1/(author_total_citation_avg*author_total_position_avg) if author_total_citation_avg and author_total_position_avg else 0
    Indexes_dict = {'author': author_name, 
                    'author_class': author_class,
                    'keyword': keyword,
                    'I1': round(I1,3),
                    'I2': round(I2,3),
                    'kpi_t3_positional_avg': round(author_t3_position_avg,3) if author_t3_position_avg else 0,
                    'kpi_t3_citation_avg': round(author_t3_citation_avg, 3) if author_t3_citation_avg else 0,
                    'kpi_total_positional_avg': round(author_total_position_avg,3) if author_total_position_avg else 0,
                    'kpi_total_citation_avg': round(author_total_citation_avg,3) if author_total_citation_avg else 0,
                    'total_citations': int(total_citations),
                    'total_citations_k': int(total_citations_k),
                    'total_articles': len(author_papers_df),
                    'total_articles_k': len(keywords_df)}
    return Indexes_dict

def normalize_name(name):
    if not isinstance(name, str):
        return ""
    name = name.strip().lower()
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))
    name = name.replace(',', '')
    name = ' '.join(name.split())
    return name

def all_name_variants(name):
    # Returns a set of possible normalized forms: "first last", "last first"
    name = name.strip()
    variants = set()
    norm = normalize_name(name)
    variants.add(norm)
    if ',' in name:
        # "Last, First" -> "First Last"
        parts = [p.strip() for p in name.split(',')]
        if len(parts) == 2:
            variants.add(normalize_name(f"{parts[1]} {parts[0]}"))
    else:
        # "First Last" -> "Last First"
        parts = name.split()
        if len(parts) >= 2:
            variants.add(normalize_name(f"{parts[-1]} {' '.join(parts[:-1])}"))
    return variants

def filter_papers_by_authors(df, author_name, column=AUTHOR_COL):
    if column not in df.columns:
        return df.iloc[0:0]
    author_variants = all_name_variants(author_name)
    def author_in_cell(cell):
        if pd.isna(cell):
            return False
        if isinstance(cell, str):
            for name in cell.split(';'):
                name = name.strip()
                if not name:
                    continue
                name_variants = all_name_variants(name)
                if author_variants & name_variants:
                    return True
        return False
    return df[df[column].apply(author_in_cell)]

def add_author_position_with_score(df, author_name, author_col=AUTHOR_COL):
    author_variants = all_name_variants(author_name)
    positions = []
    scores = []
    for authors_str in df[author_col]:
        try:
            if isinstance(authors_str, str):
                authors = [name.strip() for name in authors_str.split(';') if name.strip()]
            else:
                authors = []
            found = False
            for name in authors:
                name_variants = all_name_variants(name)
                if author_variants & name_variants:
                    pos = authors.index(name) + 1
                    positions.append(pos)
                    if pos == 1 or pos == len(authors):
                        scores.append(1.25)
                    else:
                        scores.append(1.0)
                    found = True
                    break
            if not found:
                positions.append(None)
                scores.append(None)
        except Exception:
            positions.append(None)
            scores.append(None)
    df = df.copy()
    df['author_position'] = positions
    df['author_position_score'] = scores
    return df

def filter_articles_by_keyword(df, keyword):
    keyword_slugged = keyword.lower().replace(" ", "_")
    def contains_keyword(text, keyword_slugged):
        if pd.isna(text):
            return False
        keyword_text = keyword_slugged.replace("_", " ")
        return (keyword_slugged in text.lower() or keyword_text in text.lower())
    def keyword_in_slugged_list(slugged_list_str, keyword_slugged):
        if pd.isna(slugged_list_str):
            return False
        try:
            slugged_list = ast.literal_eval(slugged_list_str) if isinstance(slugged_list_str, str) else slugged_list_str
            return keyword_slugged in [kw.lower() for kw in slugged_list]
        except:
            return False
    filtered_df = df[
        df['Article Title'].apply(lambda x: contains_keyword(str(x), keyword_slugged)) |
        df['Abstract'].apply(lambda x: contains_keyword(str(x), keyword_slugged)) |
        df[[col for col in df.columns if 'keyword' in col.lower()][0]].apply(lambda x: keyword_in_slugged_list(str(x), keyword_slugged))
    ]
    return filtered_df

def slugify_keyword(kw):
    # Lowercase, remove non-alphanumeric except spaces/hyphens, replace spaces with underscores
    kw = kw.lower()
    kw = unicodedata.normalize('NFKD', kw)
    kw = ''.join(c for c in kw if c.isalnum() or c in [' ', '-', '_'])
    kw = kw.replace(' ', '_')
    return kw

def get_keywords_for_author(df):
    keywords_set = set()
    # Use explicit keyword columns if present
    keyword_cols = []
    for col in ['Author Keywords', 'Keywords Plus']:
        if col in df.columns:
            keyword_cols.append(col)
    for idx, row in df.iterrows():
        # Extract from keyword columns
        for col in keyword_cols:
            val = row.get(col, None)
            if pd.isna(val) or val is None:
                continue
            # Try to parse as list, else split by semicolon/comma
            if isinstance(val, str):
                try:
                    lst = ast.literal_eval(val)
                    if not isinstance(lst, list):
                        raise Exception()
                except:
                    lst = re.split(r'[;,]', val)
                for kw in lst:
                    kw = kw.strip()
                    if kw and len(kw) > 2:
                        keywords_set.add(kw)
            elif isinstance(val, list):
                for kw in val:
                    kw = str(kw).strip()
                    if kw and len(kw) > 2:
                        keywords_set.add(kw)
        # Extract from title and abstract
        for col in ['Article Title', 'Abstract']:
            if col in df.columns and pd.notna(row.get(col, None)):
                text = str(row[col])
                # Tokenizar en palabras de 4+ letras
                words = re.findall(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ-]{4,}\b', text)
                # Palabras individuales
                for w in words:
                    w = w.strip()
                    if w and not re.search(r'\d', w):
                        keywords_set.add(w)
                # N-gramas de 2 palabras consecutivas
                n = 2
                for i in range(len(words) - n + 1):
                    ngram = ' '.join(words[i:i+n])
                    if all(len(word) > 3 for word in words[i:i+n]):
                        keywords_set.add(ngram)
    # Normalizar para evitar duplicados por mayúsculas/minúsculas/espacios
    keywords_norm = {}
    for kw in keywords_set:
        norm = ' '.join(kw.lower().split())
        if norm not in keywords_norm:
            keywords_norm[norm] = kw  # Mantener la forma más legible
    return sorted(keywords_norm.values(), key=lambda x: x.lower()) 