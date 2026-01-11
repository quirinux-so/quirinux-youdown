#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
# File:        youdown.py
# Author:      Charlie Martínez® <cmartinez@quirinux.org>
# License:     https://www.gnu.org/licenses/gpl-2.0.txt
# Purpose:     Descargar videos de youtube a formato MP4 y MP3
# Distro:      Quirinux 2.0, Debian Bookworm, Devuan Daedalus y derivadas
# ======================================================================

#
# Copyright (c) 2019-2025 Charlie Martínez. All Rights Reserved.  
# License: https://www.gnu.org/licenses/gpl-2.0.txt  
# Authorized and unauthorized uses of the Quirinux trademark:  
# See https://www.quirinux.org/aviso-legal  
#

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import threading
import locale
import re
from pathlib import Path

# ======================
# Traducciones (SIN CAMBIOS)
# ======================
translations = {
    'es': {
        'title': 'YouDown!',
        'url_label': 'Dirección de YouTube:',
        'format_label': 'Formato:',
        'download_button': 'Descargar',
        'footer': '© Charlie Martínez - Quirinux GPLv2',
        'select_format': ['MP4', 'MP3'],
        'success': '¡Descarga completa!',
        'error': 'Error al descargar:',
        'choose_folder': 'Selecciona carpeta de destino',
        'downloading': 'Descargando...',
    },
    'en': {
        'title': 'YouDown!',
        'url_label': 'YouTube URL:',
        'format_label': 'Format:',
        'download_button': 'Download',
        'footer': '© Charlie Martínez - Quirinux GPLv2',
        'select_format': ['MP4', 'MP3'],
        'success': 'Download completed!',
        'error': 'Download failed:',
        'choose_folder': 'Select destination folder',
        'downloading': 'Downloading...',
    },
    'de': {
        'title': 'YouDown!',
        'url_label': 'YouTube-Adresse:',
        'format_label': 'Format:',
        'download_button': 'Herunterladen',
        'footer': '© Charlie Martínez - Quirinux GPLv2',
        'select_format': ['MP4', 'MP3'],
        'success': 'Download abgeschlossen!',
        'error': 'Fehler beim Herunterladen:',
        'choose_folder': 'Zielordner auswählen',
        'downloading': 'Herunterladen...',
    },
    'fr': {
        'title': 'YouDown!',
        'url_label': 'Adresse YouTube :',
        'format_label': 'Format :',
        'download_button': 'Télécharger',
        'footer': '© Charlie Martínez - Quirinux GPLv2',
        'select_format': ['MP4', 'MP3'],
        'success': 'Téléchargement terminé !',
        'error': 'Erreur lors du téléchargement :',
        'choose_folder': 'Sélectionner le dossier de destination',
        'downloading': 'Téléchargement...',
    },
    'pt': {
        'title': 'YouDown!',
        'url_label': 'Endereço do YouTube:',
        'format_label': 'Formato:',
        'download_button': 'Baixar',
        'footer': '© Charlie Martínez - Quirinux GPLv2',
        'select_format': ['MP4', 'MP3'],
        'success': 'Download concluído!',
        'error': 'Erro ao baixar:',
        'choose_folder': 'Escolher pasta de destino',
        'downloading': 'Baixando...',
    },
    'it': {
        'title': 'YouDown!',
        'url_label': 'Indirizzo YouTube:',
        'format_label': 'Formato:',
        'download_button': 'Scarica',
        'footer': '© Charlie Martínez - Quirinux GPLv2',
        'select_format': ['MP4', 'MP3'],
        'success': 'Download completato!',
        'error': 'Errore durante il download:',
        'choose_folder': 'Seleziona cartella di destinazione',
        'downloading': 'Scaricando...',
    },
    'gl': {
        'title': 'YouDown!',
        'url_label': 'Enderezo de YouTube:',
        'format_label': 'Formato:',
        'download_button': 'Descargar',
        'footer': '© Charlie Martínez - Quirinux GPLv2',
        'select_format': ['MP4', 'MP3'],
        'success': 'Descarga completa!',
        'error': 'Erro ao descargar:',
        'choose_folder': 'Selecciona o cartafol de destino',
        'downloading': 'Descargando...',
    },
    'ru': {
        'title': 'YouDown!',
        'url_label': 'Ссылка на YouTube:',
        'format_label': 'Формат:',
        'download_button': 'Скачать',
        'footer': '© Charlie Martínez - Quirinux GPLv2',
        'select_format': ['MP4', 'MP3'],
        'success': 'Загрузка завершена!',
        'error': 'Ошибка при загрузке:',
        'choose_folder': 'Выберите папку для сохранения',
        'downloading': 'Загрузка...',
    },
    'hu': {
        'title': 'YouDown!',
        'url_label': 'YouTube URL:',
        'format_label': 'Formátum:',
        'download_button': 'Letöltés',
        'footer': '© Charlie Martínez - Quirinux GPLv2',
        'select_format': ['MP4', 'MP3'],
        'success': 'Letöltés kész!',
        'error': 'Hiba a letöltéskor:',
        'choose_folder': 'Célmappa kiválasztása',
        'downloading': 'Letöltés...',
    }
}

# ======================
# Idioma del sistema
# ======================
def get_system_language():
    loc = locale.getdefaultlocale()[0]
    if loc:
        code = loc.split('_')[0]
        return code if code in translations else 'en'
    return 'en'

# ======================
# Escritorio (XDG)
# ======================
def get_desktop_path():
    config = Path.home() / ".config/user-dirs.dirs"
    if config.exists():
        for line in config.read_text().splitlines():
            if line.startswith("XDG_DESKTOP_DIR"):
                return Path(
                    line.split("=")[1]
                    .replace("$HOME", str(Path.home()))
                    .strip('"')
                )
    return Path.home()

# ======================
# Estilo
# ======================
BG_MAIN = "#1e1e1e"
BG_PANEL = "#2a2a2a"
FG_TEXT = "#e6e6e6"
ACCENT = "#ab7ab5"

# ======================
# App
# ======================
class YoutubeDownloader:
    def __init__(self, root):
        self.root = root
        self.lang = get_system_language()
        self.t = translations[self.lang]

        self.root.title(self.t['title'])
        self.root.geometry("480x300")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        # Icono
        try:
            self.icon = tk.PhotoImage(file="/usr/share/icons/youdown.png")
            tk.Label(root, image=self.icon, bg=BG_MAIN).pack(pady=(10, 0))
            root.iconphoto(False, self.icon)
        except:
            self.icon = None

        tk.Label(
            root,
            text=self.t['title'],
            font=("Arial", 14, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT
        ).pack(pady=(4, 2))

        tk.Label(
            root,
            text=self.t['footer'],
            font=("Arial", 9),
            bg=BG_MAIN,
            fg=ACCENT
        ).pack(pady=(0, 10))

        self.url_var = tk.StringVar()
        self.format_var = tk.StringVar(value="MP4")

        tk.Label(root, text=self.t['url_label'], bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
        tk.Entry(root, textvariable=self.url_var, width=52).pack(padx=20, pady=2)

        tk.Label(root, text=self.t['format_label'], bg=BG_MAIN, fg=FG_TEXT).pack(padx=20, pady=(8, 0))
        ttk.Combobox(root, textvariable=self.format_var,
                     values=self.t['select_format'], state="readonly",  width=8).pack(padx=20)
        style = ttk.Style(self.root)

        # Forzar uso de tema que permita colores (importante en Linux)
        style.theme_use('default')

        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor="#2a2a2a",   # fondo (oscuro, acorde al tema)
            background="#7bd88f",    # verde claro (barra)
            thickness=24
        )

        self.progress = ttk.Progressbar(
            root,
            length=360,
            mode="determinate",
            style="Green.Horizontal.TProgressbar"
        )

        self.progress.pack(pady=10)

        tk.Button(
            root,
            text=self.t['download_button'],
            command=self.start_download_thread,
            bg=BG_PANEL,
            fg=FG_TEXT,
            activebackground=ACCENT,
            activeforeground=BG_MAIN,
            relief="flat",
            padx=20,
            pady=8
        ).pack()

        self.status_label = tk.Label(root, text="", bg=BG_MAIN, fg=ACCENT)
        self.status_label.pack(pady=4)

    def start_download_thread(self):
        threading.Thread(target=self.download_video, daemon=True).start()

    def download_video(self):
        url = self.url_var.get().strip()
        fmt = self.format_var.get().lower()

        if not url:
            messagebox.showerror(self.t['title'], self.t['error'])
            return

        folder = filedialog.askdirectory(
            title=self.t['choose_folder'],
            initialdir=get_desktop_path(),
            mustexist=True
        )
        if not folder:
            return

        self.status_label.config(text=self.t['downloading'])
        self.progress['value'] = 0

        try:
            if fmt == "mp4":
                cmd = [
                    "yt-dlp",
                    "-f", "bestvideo+bestaudio",
                    "--merge-output-format", "mp4",
                    "-o", os.path.join(folder, "%(title)s.%(ext)s"),
                    url
                ]
            else:
                cmd = [
                    "yt-dlp",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "-o", os.path.join(folder, "%(title)s.%(ext)s"),
                    url
                ]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in process.stdout:
                match = re.search(r"(\d{1,3}\.\d)%", line)
                if match:
                    self.progress['value'] = float(match.group(1))
                    self.root.update_idletasks()

            process.wait()

            if process.returncode == 0:
                self.progress['value'] = 100
                messagebox.showinfo(self.t['title'], self.t['success'])
                self.status_label.config(text=self.t['success'])
            else:
                raise RuntimeError("yt-dlp error")

        except Exception as e:
            messagebox.showerror(self.t['title'], f"{self.t['error']}\n{e}")

# ======================
if __name__ == "__main__":
    root = tk.Tk()
    YoutubeDownloader(root)
    root.mainloop()
