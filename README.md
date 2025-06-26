# Author Index Related to the Keyword Metric
---

## Overview

This software is a desktop application for calculating the **Absolute Author Index (AIa)** and **Relative Author Index (AIr)** for researchers, based on a selected keyword. These indices allow for the evaluation of a researcher's performance within a specific scientific field, as defined by the chosen keyword (e.g., "Quantum Information").

The application is built with Python and uses the `tkinter` and `customtkinter` libraries for its graphical user interface. It is intended for scientometric analysis and supports the import, management, and analysis of publication data for multiple authors.

![Author Index Related to the Keyword Metric Calculator](/resources/example.png)

## Features

- **User-friendly GUI**: Modern, intuitive interface using `customtkinter`.
- **Multi-author support**: Add and manage publication data for any number of authors.
- **Keyword-based analysis**: Calculate indices for any keyword present in the authors' publications.
- **Word Cloud Visualization**: Instantly visualize the most frequent keywords for each author.
- **Detailed Metrics**: View comprehensive statistics, including citation averages, positional averages, and article counts.
- **Data import**: Import publication data exported from Web of Science (CSV or Excel format).
- **Extensible and modular**: Clean, modular codebase for easy extension and adaptation.



## How It Works

1. **Data Import**: Users import publication data for each author (downloaded from Web of Science) via the GUI.
2. **Author & Keyword Selection**: Select an author and a keyword to analyze.
3. **Index Calculation**: The application computes:
   - **AIa (Absolute Author Index)**: Based on the top 3 cited articles containing the keyword, considering author position.
   - **AIr (Relative Author Index)**: Normalizes AIa by the author's overall performance.
4. **Visualization**: Results are displayed numerically and visually (word cloud, tables).
5. **Details**: Users can view detailed metrics, including citation and positional averages, and article counts.

## Data Requirements

- **Input Format**: Publication data must be exported from Web of Science in CSV or Excel format.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd Author-Index-Related-to-the-Keyword-Metric
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Execute Pyinstaller**:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --add-data "media;media" app/main.py
   ```

**Note:** You can use instead the pre-compile provided executable inside the `desktop` folder



## Example Workflow

1. **Add Author Data**: Use "Upload New Author Data" to add publication files for a new author.
2. **Select Author**: Choose an author from the list.
3. **Select/Type Keyword**: Enter or select a keyword relevant to the author's publications.
4. **Calculate Indices**: Click "Calculate Indices" to view AIa and AIr.
5. **View Details**: Click "View Details" for a breakdown of metrics.



## Details

- **Author Name Normalization**: The application uses robust normalization to match author names across different formats (e.g., "Last, First" vs. "First Last").
- **Keyword Extraction**: Keywords are extracted from explicit fields ("Author Keywords", "Keywords Plus") and from the title/abstract text, supporting both list and string formats.
- **Position Score**: The index calculation considers the author's position in the author list, giving extra weight to first/last authors.



## Authors

- Jorge Felix Martinez Pazos
- Jorge Gulin Gonzales  
  Study Center on Computational Mathematics  
  University of Informatics Science, Havana, Cuba



## License

This project is licensed under the MIT License.
