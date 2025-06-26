# Lógica para cargar y validar archivos Excel o CSV

import sys
import os
import shutil
import pandas as pd

# --- NUEVO: Gestión profesional de carpeta de datos persistente ---
def get_persistent_data_dir():
    """Obtiene la ruta de la carpeta persistente de datos en Documentos/AuthorIndexData."""
    if os.name == 'nt':  # Windows
        docs = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Documents')
    else:
        docs = os.path.join(os.path.expanduser('~'), 'Documents')
    data_dir = os.path.join(docs, 'AuthorIndexData')
    # Si no existe, copiar los datos iniciales
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        # Copiar datos iniciales desde media/data (junto al bundle o script)
        initial_data = resource_path(os.path.join('media', 'data'))
        if os.path.exists(initial_data):
            for author in os.listdir(initial_data):
                src_author_dir = os.path.join(initial_data, author)
                dst_author_dir = os.path.join(data_dir, author)
                if os.path.isdir(src_author_dir):
                    shutil.copytree(src_author_dir, dst_author_dir, dirs_exist_ok=True)
    return data_dir

# --- FIN NUEVO ---

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, compatible con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

def load_file(filepath):
    # Implementar la lógica de carga y validación
    pass

def save_file_for_author(author, file_path, base_dir=None):
    if base_dir is None:
        base_dir = get_persistent_data_dir()
    author_dir = os.path.join(base_dir, author)
    os.makedirs(author_dir, exist_ok=True)
    filename = os.path.basename(file_path)
    dest_path = os.path.join(author_dir, filename)
    shutil.copy2(file_path, dest_path)
    return dest_path

def load_all_data(base_dir=None):
    if base_dir is None:
        base_dir = get_persistent_data_dir()
    all_dfs = []
    for author in os.listdir(base_dir):
        author_dir = os.path.join(base_dir, author)
        if os.path.isdir(author_dir):
            for fname in os.listdir(author_dir):
                fpath = os.path.join(author_dir, fname)
                if fname.endswith('.csv'):
                    df = pd.read_csv(fpath)
                elif fname.endswith('.xlsx') or fname.endswith('.xls'):
                    df = pd.read_excel(fpath)
                else:
                    continue
                df['__author__'] = author
                all_dfs.append(df)
    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    else:
        return pd.DataFrame()

if __name__ == '__main__':
    base_dir = resource_path(os.path.join('media', 'data'))
    for author in os.listdir(base_dir):
        author_dir = os.path.join(base_dir, author)
        if os.path.isdir(author_dir):
            for fname in os.listdir(author_dir):
                fpath = os.path.join(author_dir, fname)
                if fname.endswith('.csv'):
                    df = pd.read_csv(fpath)
                elif fname.endswith('.xlsx') or fname.endswith('.xls'):
                    df = pd.read_excel(fpath)
                else:
                    continue
                print(f'--- {author}/{fname} ---')
                print('Columns:', df.columns.tolist())
                for col in ['Author Keywords', 'Keywords Plus', 'Article Title', 'Abstract']:
                    if col in df.columns:
                        non_empty = df[col].dropna()
                        val = non_empty.iloc[0] if not non_empty.empty else '(empty)'
                        print(f'  {col}: {val}')
                    else:
                        print(f'  {col}: (missing)') 