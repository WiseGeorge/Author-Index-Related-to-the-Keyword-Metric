import customtkinter as ctk
from app.gui.styles import BACKGROUND_COLOR, PRIMARY_COLOR
from app.logic.file_loader import load_all_data
from wordcloud import WordCloud
from PIL import Image, ImageTk
import numpy as np

FIXED_WIDTH = 400
FIXED_HEIGHT = 300

class WordCloudViewer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BACKGROUND_COLOR, width=FIXED_WIDTH, height=FIXED_HEIGHT)
        self.pack_propagate(False)
        self.label = ctk.CTkLabel(self, text="Keyword Cloud", font=("Segoe UI", 12, "bold"), text_color=PRIMARY_COLOR)
        self.label.pack(pady=5)
        self.canvas = None
        self.current_author = None

    def show_for_author(self, author):
        self.current_author = author
        self._draw_wordcloud()

    def _draw_wordcloud(self):
        df = load_all_data()
        if df.empty or '__author__' not in df.columns or not self.current_author:
            return
        df_author = df[df['__author__'] == self.current_author]
        text = ''
        for _, row in df_author.iterrows():
            text += str(row.get('Article Title', '')) + ' '
            text += str(row.get('Abstract', '')) + ' '
        if not text.strip():
            text = 'No enough data.'
        wc = WordCloud(width=FIXED_WIDTH, height=FIXED_HEIGHT, background_color='white', colormap='Blues', margin=0).generate(text)
        img = wc.to_array()
        pil_img = Image.fromarray(img)
        tk_img = ImageTk.PhotoImage(pil_img)

        # Si ya hay una imagen previa, destrúyela
        if hasattr(self, 'img_label') and self.img_label:
            self.img_label.destroy()

        self.img_label = ctk.CTkLabel(self, image=tk_img, text="")
        self.img_label.image = tk_img  # Guarda referencia para evitar garbage collection
        self.img_label.pack(fill='both', expand=True) 