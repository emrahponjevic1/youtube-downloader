import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import random
import threading
import re
import queue
import time
import pathlib
import shutil
import subprocess
import ctypes
import sys
import psutil
from collections import defaultdict
from itertools import zip_longest
import math
import webbrowser       
import certifi
import ssl  # Obavezno importujte ssl

# --- MONKEY PATCH ZA ZAOBILAŽENJE SVIH SSL GREŠAKA ---
# UPOZORENJE: Ovo globalno isključuje provjeru SSL certifikata za cijelu aplikaciju.
# Koristiti samo kada je neophodno, kao u ovom slučaju.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Python < 2.7.9 / 3.4 nema ovu provjeru, pa je ignorišemo.
    pass
else:
    # "Zakrpi" ssl modul da koristi neprovjereni kontekst kao default.
    ssl._create_default_https_context = _create_unverified_https_context
# --- KRAJ MONKEY PATCH-a ---

# --- BLOK KODA ZA "SELF-ELEVATION" ---
def is_admin():
    """Provjerava da li se skripta izvršava sa administratorskim pravima."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    """Ponovo pokreće skriptu sa administratorskim pravima."""
    # Koristi se ShellExecuteW za bolju podršku Unicode putanjama
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# Glavna provjera na startu programa
if os.name == 'nt':
    if not is_admin():
        print("Attempting to re-launch with admin privileges...")
        run_as_admin()
        sys.exit() # Ugasi originalni, ne-administratorski proces
        
# --- GLOBALNA KONFIGURACIJA PUTANJE ZA FFmpeg ---
def setup_ffmpeg_path():
    """
    Dodaje putanju do ffmpeg binarnih fajlova u sistemski PATH.
    Ovo radi i za .py i za .exe verziju.
    """
    # Prvo, dobijemo osnovnu putanju (ili _MEIPASS ili trenutni direktorij)
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    # Kreiramo punu putanju do ffmpeg_binaries foldera
    ffmpeg_path = os.path.join(base_path, "ffmpeg_binaries")
    
    # Dodajemo ovu putanju na početak sistemskog PATH-a
    # `os.pathsep` je separator (';' na Windows-u)
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]
    print(f"FFmpeg path added to PATH: {ffmpeg_path}")

# Pozivamo funkciju odmah na startu programa
setup_ffmpeg_path()
# --- KRAJ GLOBALNE KONFIGURACIJE ---

def resource_path(relative_path):
    """
    Vraća apsolutnu putanju do resursa, radi i za dev i za .exe.
    Ovo je najpouzdaniji način.
    """
    try:
        # PyInstaller kreira temp folder i sprema putanju u _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Ako nismo spakovani, base_path je folder gdje se nalazi skripta
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Available Themes ---
AVAILABLE_THEMES = [
    'flatly', 'journal', 'pulse', 'minty', 'lumen', 
    'solar', 'cyborg', 'vapor', 'superhero', 'darkly',
    'cosmo', 'sandstone'
]

# --- Translations ---
translations = {
    "Bosanski": {
        "app_title": "YouTube Downloader by emrah-dev.net",
        "youtube_link": "YouTube link/lista (zalijepi link):",
        "language": "Jezik:",
        "download": "💾 PREUZMI",
        "stop": "✋ ZAUSTAVI",
        "error": "Greška",
        "error_no_link": "Molim unesite validan YouTube link ili playlistu.",
        "error_no_folder": "Molim izaberite direktorij za spremanje.",
        "status_waiting": "Status: Čekam unos...",
        "status_downloading": "Preuzimanje... {percent:.0f}%",
        "status_finished": "Preuzimanje završeno!",
        "status_start": "Pokrećem preuzimanje...",
        "status_stopped": "Preuzimanje zaustavljeno!",
        "options": "OPCIJE PREUZIMANJA",
        "media_audio": "Audio",
        "media_video": "Video",
        "format": "Format:",
        "bitrate": "Bitrate:",
        "resolution": "Rezolucija:",
        "extra_options": "Dodatne opcije",
        "normalize_audio": "Normaliziraj glasnoću",
        "choose_folder": "Odaberi direktorij",
        "list_for_download": "LISTA ZA PREUZIMANJE",
        "randomize_section": "OPERACIJE SA DATOTEKAMA",
        "choose_folder_random": "Odaberi folder",
        "randomize_button": "Randomiziraj i serijaliziraj",
        "remove_serial_button": "Ukloni serijalizaciju",
        "randomize_method": "Metoda:",
        "alphabetical": "Abecedno",
        "by_artist": "Po izvođaču",
        "random": "Nasumično",
        "error_no_files": "Folder je prazan.",
        "success_randomize": "Randomizacija i serijalizacija završena!",
        "success_remove_serial": "Uklanjanje serijalizacije završeno!",
        "success_download": "Preuzimanje završeno!",
        "success_message": "Želite li otvoriti folder sa preuzetim datotekama?",
        "error_rename": "Ne mogu preimenovati {file}:\n{error}",
        "status_analyzing": "Analiza linkova i ubacivanje... (može potrajati)",
        "column_no": "Br.",
        "column_file": "File/URL",
        "column_status": "Status",
        "status_playlist_item": "Pregled stavke {current}/{total}",
        "error_playlist_item": "Preskačem nevažeću stavku",
        "error_video_format": "Greška pri preuzimanju videa: {error}",
        "status_completed": "Završeno",
        "status_error": "Greška",
        "converted_label": "Konvertirano: {}/{}",
        "status_converting": "Konvertiranje...",
        "status_file_check": "Provjera datoteke...",
        "file_check_failed": "Datoteka nije pronađena: {}",
        "status_download_complete": "Preuzimanje završeno",
        "import_label": "ili uvezi iz datoteke (.txt)",
        "import_button": "UVEZI IZ TXT",
        "import_success": "Uvezeno {} linkova",
        "import_error": "Greška pri uvozu",
        "import_empty": "Datoteka je prazna ili nema validnih linkova",
        "usb_burning": "USB BURNING",
        "select_usb": "Izaberi USB uređaj:",
        "refresh": "Osvježi",
        "burn_usb": "🔥 BURN NA USB",
        "burning": "Burning na USB...",
        "burn_complete": "USB Burning završen!",
        "ejecting": "Sigurno izbacujem USB...",
        "usb_ejected": "USB Media izbačen!",
        "confirm_burn": "Ovo će izbrisati SVE podatke na {}!\nJeste li sigurni da želite nastaviti?",
        "no_usb": "Nema USB uređaja",
        "select_folder": "Molim izaberite direktorij za burning.",
        "choose_burn_folder": "Izaberite Folder",
        "burn_folder": "Folder za burning:",
        "burn_progress": "Burning: {copied}/{total} datoteka",
        "preparing_structure": "Pripremam strukturu za auto-reprodukciju...",
        "creating_autoplay": "Kreiram auto-play datoteke...",
        "writing_metadata": "Pišem informacije o pjesmama...",
        "error_no_files": "Nema muzičkih datoteka u folderu",
        "error_metadata": "Ne mogu napisati metapodatke za: {}",
        "autorun_created": "Auto-play konfigurisan za auto radio!",
        "usb_ready": "USB je spreman za korištenje u automobilu!",
        "admin_format_required": "Administratorski privilegiji su potrebni za formatiranje. Pokrenite aplikaciju kao administrator.",
        "error_file_empty": "Greška: Preuzeta datoteka je prazna! Video možda nije dostupan, privatni je, ili je zaštićen autorskim pravima.",
        "error_private_video": "Greška: Video je privatni ili uklonjen.",
        "error_geo_restricted": "Greška: Video nije dostupan u vašoj regiji.",
        "status_retrying": "Ponovno pokušavam ({attempt}/{max_attempts})...",
        "status_failed_after_retries": "Greška: Neuspjelo nakon {max_attempts} pokušaja",
        "status_waiting_item": "Čekanje",
        "status_downloading_item": "Preuzimanje",
        "status_converting_item": "Konvertiranje",
        "status_completed_item": "Završeno",
        "status_error_item": "Greška",
        "status_stopped_item": "Zaustavljeno",
        "invalid_item": "Nevažeća stavka",
        "folder_empty": "Folder je prazan",
        "usb_format_failed": "Formatiranje USB uređaja nije uspjelo",
        "usb_structure_failed": "Kreiranje strukture nije uspjelo",
        "copy_failed": "Kopiranje datoteka nije uspjelo",
        "usb_eject_failed": "Izbacivanje USB uređaja nije uspjelo",
        "usb_features": "Karakteristike uključuju:\n- FAT32 format za kompatibilnost\n- Auto-play podrška\n- Poboljšani metapodaci\n- Organizirana struktura\n- Glavna playlist",
        "admin_required": "Potrebni administratorski privilegiji",
        "processing_item": "Obrada stavke",
        "video": "Video",
        "file_not_found": "Datoteka nije pronađena",
        "invalid_url": "Nevažeći URL",
        "starting_download": "Početak preuzimanja",
        "downloading": "Preuzimanje",
        "converting": "Konvertiranje",
        "download_success": "Preuzimanje uspješno",
        "download_failed": "Preuzimanje neuspješno",
        "all_done": "Sve završeno",
        "usb_not_found": "USB uređaj nije pronađen",
        "source_folder_error": "Greška u izvornom folderu",
        "usb_selection_error": "Greška u odabiru USB uređaja",
        "burning_started": "Burning započeo",
        "formatting": "Formatiranje",
        "creating_structure": "Kreiranje strukture",
        "copying_files": "Kopiranje datoteka",
        "enhancing_metadata": "Poboljšavanje metapodataka",
        "finalizing": "Finaliziranje",
        "ejecting_usb": "Izbacivanje USB uređaja",
        "operation_complete": "Operacija završena",
        "file_operations": "Operacije sa datotekama",
        "serialization": "Serijalizacija",
        "deserialization": "Deserijalizacija",
        "folder_selection": "Odabir foldera",
        "download_options": "Opcije preuzimanja",
        "media_type": "Vrsta medija",
        "audio_format": "Audio format",
        "video_format": "Video format",
        "quality_settings": "Postavke kvalitete",
        "normalization": "Normalizacija",
        "download_list": "Lista za preuzimanje",
        "progress": "Napredak",
        "conversion_status": "Status konverzije",
        "system_status": "Sistemski status",
        "actions": "Akcije",
        "usb_operations": "USB operacije",
        "drive_selection": "Odabir uređaja",
        "burn_process": "Proces burninga",
        "file_management": "Upravljanje datotekama",
        "sorting_method": "Metoda sortiranja",
        "randomization": "Randomizacija",
        "status": "Status",
        "item": "Stavka",
        "url": "URL",
        "no": "Br.",
        "file": "Datoteka",
        "percent_complete": "Procentualno završeno",
        "total_items": "Ukupno stavki",
        "completed_items": "Završene stavke",
        "queue": "Red",
        "playlist": "Playlista",
        "single_video": "Pojedinačni video",
        "attempt": "Pokušaj",
        "max_attempts": "Maksimalni pokušaji",
        "retrying": "Ponovni pokušaj",
        "failed": "Neuspješno",
        "succeeded": "Uspješno",
        "stopped": "Zaustavljeno",
        "waiting": "Čekanje",
        "analyzing": "Analiziranje",
        "import": "Uvoz",
        "export": "Izvoz",
        "burn": "Burn",
        "eject": "Izbaci",
        "refresh": "Osvježi",
        "start": "Pokreni",
        "cancel": "Otkaži",
        "open_folder": "Otvori folder",
        "rename": "Preimenuj",
        "serialize": "Serializiraj",
        "remove_serial": "Ukloni serijalizaciju",
        "choose": "Odaberi",
        "select": "Izaberi",
        "confirm": "Potvrdi",
        "continue": "Nastavi",
        "back": "Nazad",
        "exit": "Izlaz",
        "help": "Pomoć",
        "about": "O programu",
        "settings": "Postavke",
        "language_settings": "Postavke jezika",
        "appearance": "Izgled",
        "theme": "Tema",
        "light": "Svijetla",
        "dark": "Tamna",
        "system_default": "Sistemska zadana",
        "advanced": "Napredno",
        "basic": "Osnovno",
        "simple": "Jednostavno",
        "expert": "Stručno",
        "beginner": "Početnički",
        "user_interface": "Korisničko sučelje",
        "functionality": "Funkcionalnost",
        "performance": "Performanse",
        "storage": "Pohrana",
        "usb_device": "USB uređaj",
        "drive": "Pogon",
        "partition": "Particija",
        "file_system": "Datotečni sustav",
        "auto_play": "Auto-play",
        "metadata": "Metapodaci",
        "id3_tags": "ID3 tagovi",
        "audio_properties": "Svojstva audio datoteka",
        "video_properties": "Svojstva video datoteka",
        "codec": "Kodek",
        "bit_depth": "Dubina bita",
        "sample_rate": "Brzina uzorkovanja",
        "frame_rate": "Brzina kadrova",
        "resolution": "Rezolucija",
        "aspect_ratio": "Omjer slike",
        "duration": "Trajanje",
        "file_size": "Veličina datoteke",
        "format": "Format",
        "container": "Kontejner",
        "extension": "Ekstenzija",
        "filename": "Naziv datoteke",
        "directory": "Direktorij",
        "path": "Putanja",
        "size": "Veličina",
        "date_modified": "Datum izmjene",
        "date_created": "Datum kreiranja",
        "attributes": "Atributi",
        "permissions": "Dozvole",
        "owner": "Vlasnik",
        "group": "Grupa",
        "hidden": "Skriveno",
        "read_only": "Samo za čitanje",
        "system_file": "Sistemska datoteka",
        "archive": "Arhiva",
        "compressed": "Komprimirano",
        "encrypted": "Šifrirano",
        "temporary": "Privremeno",
        "offline": "Offline",
        "not_content_indexed": "Nije indeksirano",
        "integrity_stream": "Struja integriteta",
        "no_scrub_data": "Bez podataka za čišćenje",
        "virtual": "Virtualno",
        "tab_download": "PREUZIMANJE",
        "tab_randomize": "RANDOMIZACIJA",
        "tab_burning": "USB BURNING",
        "file_list": "Lista datoteka",
        "original_name": "Originalni naziv",
        "new_name": "Novi naziv",
        "loading_files": "Učitavam datoteke...",
        "files_loaded": "Učitano datoteka: {}",
        "renaming_files": "Preimenujem datoteke...",
        "serialization_removed": "Serijski brojevi uklonjeni",
        "theme": "Tema",
        "donation_title": "Podrži razvoj",
        "donation_message": "Hvala što koristite naš besplatan softver!\n\nAko vam se sviđa ovaj program i želite podržati daljnji razvoj, razmislite o donaciji. Svaka donacija, ma koliko mala, pomaže u održavanju i poboljšanju ovog alata.\n\nŽelite li posjetiti našu stranicu za donacije?",
        "donation_yes": "Da, želim podržati",
        "donation_no": "Ne, hvala",
        "donation_thanks": "Hvala na podršci!",
        "program_description": "Opis programa",
        "about_description_text": "Ovaj YouTube Downloader vam omogućuje:\n- Preuzimanje video i audio sadržaja sa YouTube-a\n- Obrada playlista i više linkova odjednom\n- Randomizacija i organizacija muzičkih datoteka\n- Kreiranje USB uređaja optimiziranih za auto audio sisteme\n\nKarakteristike:\n✔ Podrška za više formata i kvaliteta\n✔ Obrada više datoteka odjednom\n✔ Višejezička podrška\n✔ Čisto i intuitivno sučelje",
        "how_to_use": "Kako koristiti",
        "usage_instructions_text": "1. PREUZIMANJE TAB:\n   - Zalijepite YouTube link(ove) u polje za unos\n   - Odaberite opcije preuzimanja (audio/video, format, kvalitet)\n   - Odaberite odredišni folder\n   - Kliknite PREUZMI dugme\n\n2. RANDOMIZACIJA TAB:\n   - Odaberite folder sa vašim datotekama\n   - Odaberite metodu randomizacije\n   - Kliknite Randomiziraj ili Ukloni serijalizaciju\n\n3. USB BURNING TAB:\n   - Odaberite izvorni folder sa muzikom\n   - Odaberite USB uređaj\n   - Kliknite BURN NA USB",
        "developer_info": "Informacije o developeru",
        "developer_info_text": "Kreirano sa ❤️ od strane [Vaše ime]\n\nPronađite me na:\n• GitHub: github.com/vašikorisničkoime\n• LinkedIn: linkedin.com/in/vašprofil\n• Web stranica: vašastranica.com\n\nZa podršku ili zahtjeve za nove funkcije:\n✉️ vaš.email@example.com",
        "support_project": "Podržite ovaj projekat",
        "donation_appeal_text": "Ako vam se ovaj softver sviđa, razmislite o podršci njegovog razvoja.\nVaša donacija pomaže u održavanju i poboljšanju ovog alata.",
        "donate_now": "Doniraj sada",
        "tab_about": "O PROGRAMU",
        "program_description": "Opis programa",
        "about_description_left": "Ovaj YouTube Downloader vam omogućava:\n- Preuzimanje video i audio sadržaja sa YouTube-a\n- Obrada playlista i više linkova odjednom\n- Randomizacija i organizacija muzičkih datoteka\n- Kreiranje USB uređaja optimiziranih za auto audio sisteme",
        "about_features_right": "Karakteristike:\n✔ Podrška za više formata i kvaliteta\n✔ Obrada više datoteka odjednom\n✔ Višejezička podrška\n✔ Čisto i intuitivno sučelje\n✔ Brzo preuzimanje sa više niti\n✔ Sistem za oporavak od grešaka\n✔ Mogućnost burninga na USB",
        "how_to_use": "Kako koristiti",
        "usage_instructions_text": "1. PREUZIMANJE TAB:\n   - Zalijepite YouTube link(ove) u polje za unos\n   - Odaberite opcije preuzimanja (audio/video, format, kvalitet)\n   - Odaberite odredišni folder\n   - Kliknite PREUZMI dugme\n\n2. RANDOMIZACIJA TAB:\n   - Odaberite folder sa vašim datotekama\n   - Odaberite metodu randomizacije\n   - Kliknite Randomiziraj ili Ukloni serijalizaciju\n\n3. USB BURNING TAB:\n   - Odaberite izvorni folder sa muzikom\n   - Odaberite USB uređaj\n   - Kliknite BURN NA USB",
        "developer_info": "Informacije o developeru",
        "developer_info_text": "Kreirano sa ❤️ od strane Emrah Ponjevic\n\nPronađite me na:\n• GitHub: github.com/emrahponjevic\n• LinkedIn: linkedin.com/in/emrahponjevic\n\nZa podršku ili zahtjeve za nove funkcije:\n✉️ emrah.ponjevic@gmail.com",
        "support_project": "Podržite ovaj projekat",
        "donation_appeal_text": "Ako vam se ovaj softver sviđa, razmislite o podršci njegovog razvoja.\nVaša donacija pomaže u održavanju i poboljšanju ovog alata.",
        "donate_now": "Doniraj sada",
        "tab_about": "O PROGRAMU",
        "version_info": "YouTube Downloader v1.0",
         "tab_about": "O PROGRAMU",
        "program_description": "Opis programa",
        "about_description_left": "Ovaj YouTube Downloader vam omogućava:\n\n- Preuzimanje video i audio sadržaja sa YouTube-a\n- Obrada playlista i više linkova odjednom\n- Randomizacija i organizacija muzičkih datoteka\n- Kreiranje USB uređaja optimiziranih za auto audio sisteme",
        "about_features_right": "Karakteristike:\n✔ Podrška za više formata i kvaliteta\n✔ Obrada više datoteka odjednom\n✔ Višejezička podrška\n✔ Čisto i intuitivno sučelje\n✔ Brzo preuzimanje sa više niti\n✔ Sistem za oporavak od grešaka\n✔ Mogućnost burninga na USB",
        "how_to_use": "Kako koristiti",
        "usage_instructions_text": "1. PREUZIMANJE TAB:\n   - Zalijepite YouTube URL(s) u polje za unos\n   - Odaberite opcije preuzimanja (audio/video, format, kvalitet)\n   - Odaberite odredišni folder\n   - Kliknite PREUZMI dugme\n\n2. RANDOMIZACIJA TAB:\n   - Odaberite folder sa vašim datotekama\n   - Odaberite metodu randomizacije\n   - Kliknite Randomiziraj ili Ukloni serijalizaciju\n\n3. USB BURNING TAB:\n   - Odaberite izvorni folder sa muzikom\n   - Odaberite USB uređaj\n   - Kliknite BURN NA USB",
        "developer_info": "Informacije o developeru",
        "developer_info_text": "Kreirano sa ♡ od strane Emrah Ponjevic\n\nPronađite me na:\n GitHub: github.com/emrahponjevic\n• LinkedIn: linkedin.com/in/emrahponjevic\n\nZa podršku ili zahtjeve za nove funkcije:\n✉️ emrah.ponjevic@gmail.com",
        "support_project": "Podržite ovaj projekat",
        "donation_appeal_text": "Ako vam se ovaj softver sviđa, razmislite o podršci njegovog razvoja.\nVaša donacija pomaže u održavanju i poboljšanju ovog alata.",
        "donate_now": "Doniraj sada",
        "GitHub": "GitHub",
        "LinkedIn": "LinkedIn",
        "version_info": "YouTube Downloader v1.0"
    },
    "English": {
        "app_title": "YouTube Downloader by emrah-dev.net",
        "youtube_link": "YouTube link/playlist (paste link):",
        "language": "Language:",
        "download": "💾 DOWNLOAD",
        "stop": "✋ STOP",
        "error": "Error",
        "error_no_link": "Please enter a valid YouTube link or playlist.",
        "error_no_folder": "Please select a folder to save.",
        "status_waiting": "Status: Waiting for input...",
        "status_downloading": "Downloading... {percent:.0f}%",
        "status_finished": "Download completed!",
        "status_start": "Starting download...",
        "status_stopped": "Download stopped!",
        "options": "DOWNLOAD OPTIONS",
        "media_audio": "Audio",
        "media_video": "Video",
        "format": "Format:",
        "bitrate": "Bitrate:",
        "resolution": "Resolution:",
        "extra_options": "Extra options",
        "normalize_audio": "Normalize volume",
        "choose_folder": "Choose folder",
        "list_for_download": "DOWNLOAD QUEUE",
        "randomize_section": "FILE OPERATIONS",
        "choose_folder_random": "Choose folder",
        "randomize_button": "Randomize and serialize",
        "remove_serial_button": "Remove serialization",
        "randomize_method": "Method:",
        "alphabetical": "Alphabetical",
        "by_artist": "By artist",
        "random": "Random",
        "error_no_files": "Folder is empty.",
        "success_randomize": "Randomization and serialization done!",
        "success_remove_serial": "Serialization removal done!",
        "success_download": "Download complete!",
        "success_message": "Do you want to open the download folder?",
        "error_rename": "Cannot rename {file}:\n{error}",
        "status_analyzing": "Analyzing links and importing... (this may take a while)",
        "column_no": "No.",
        "column_file": "File/URL",
        "column_status": "Status",
        "status_playlist_item": "Processing item {current}/{total}",
        "error_playlist_item": "Skipping invalid item",
        "error_video_format": "Video download error: {error}",
        "status_completed": "Completed",
        "status_error": "Error",
        "converted_label": "Converted: {}/{}",
        "status_converting": "Converting...",
        "status_file_check": "Checking file...",
        "file_check_failed": "File not found: {}",
        "status_download_complete": "Download complete",
        "import_label": "or import from file (.txt)",
        "import_button": "IMPORT FROM TXT",
        "import_success": "Imported {} links",
        "import_error": "Import error",
        "import_empty": "File is empty or contains no valid links",
        "usb_burning": "USB BURNING",
        "select_usb": "Select USB Drive:",
        "refresh": "Refresh",
        "burn_usb": "🔥 BURN TO USB",
        "burning": "Burning to USB...",
        "burn_complete": "USB Burning Complete!",
        "ejecting": "Ejecting USB safely...",
        "usb_ejected": "USB Media ejected!",
        "confirm_burn": "This will erase ALL data on {}!\nAre you sure you want to continue?",
        "no_usb": "No USB drives found",
        "select_folder": "Please select a folder to Burn.",
        "choose_burn_folder": "Choose Folder",
        "burn_folder": "Burn Folder:",
        "burn_progress": "Burning: {copied}/{total} files",
        "preparing_structure": "Preparing auto-play structure...",
        "creating_autoplay": "Creating auto-play files...",
        "writing_metadata": "Writing track information...",
        "error_no_files": "No music files found in folder",
        "error_metadata": "Couldn't write metadata for: {}",
        "autorun_created": "Auto-play configured for car radios!",
        "usb_ready": "USB is ready for car use!",
        "admin_format_required": "Admin privileges required for formatting. Run app as administrator.",
        "error_file_empty": "ERROR: Downloaded file is empty! Video might be unavailable, private, or copyright restricted.",
        "error_private_video": "ERROR: Video is private or removed.",
        "error_geo_restricted": "ERROR: Video not available in your region.",
        "status_retrying": "Retrying ({attempt}/{max_attempts})...",
        "status_failed_after_retries": "ERROR: Failed after {max_attempts} attempts",
        "status_waiting_item": "Waiting",
        "status_downloading_item": "Downloading",
        "status_converting_item": "Converting",
        "status_completed_item": "Completed",
        "status_error_item": "Error",
        "status_stopped_item": "Stopped",
        "invalid_item": "Invalid item",
        "folder_empty": "Folder is empty",
        "usb_format_failed": "USB formatting failed",
        "usb_structure_failed": "Structure creation failed",
        "copy_failed": "File copy failed",
        "usb_eject_failed": "USB ejection failed",
        "usb_features": "Features include:\n- FAT32 format for compatibility\n- Auto-play support\n- Enhanced metadata\n- Organized structure\n- Master playlist",
        "admin_required": "Admin privileges required",
        "processing_item": "Processing item",
        "video": "Video",
        "file_not_found": "File not found",
        "invalid_url": "Invalid URL",
        "starting_download": "Starting download",
        "downloading": "Downloading",
        "converting": "Converting",
        "download_success": "Download success",
        "download_failed": "Download failed",
        "all_done": "All done",
        "usb_not_found": "USB device not found",
        "source_folder_error": "Source folder error",
        "usb_selection_error": "USB selection error",
        "burning_started": "Burning started",
        "formatting": "Formatting",
        "creating_structure": "Creating structure",
        "copying_files": "Copying files",
        "enhancing_metadata": "Enhancing metadata",
        "finalizing": "Finalizing",
        "ejecting_usb": "Ejecting USB",
        "operation_complete": "Operation complete",
        "file_operations": "File operations",
        "serialization": "Serialization",
        "deserialization": "Deserialization",
        "folder_selection": "Folder selection",
        "download_options": "Download options",
        "media_type": "Media type",
        "audio_format": "Audio format",
        "video_format": "Video format",
        "quality_settings": "Quality settings",
        "normalization": "Normalization",
        "download_list": "Download list",
        "progress": "Progress",
        "conversion_status": "Conversion status",
        "system_status": "System status",
        "actions": "Actions",
        "usb_operations": "USB operations",
        "drive_selection": "Drive selection",
        "burn_process": "Burn process",
        "file_management": "File management",
        "sorting_method": "Sorting method",
        "randomization": "Randomization",
        "status": "Status",
        "item": "Item",
        "url": "URL",
        "no": "No.",
        "file": "File",
        "percent_complete": "Percent complete",
        "total_items": "Total items",
        "completed_items": "Completed items",
        "queue": "Queue",
        "playlist": "Playlist",
        "single_video": "Single video",
        "attempt": "Attempt",
        "max_attempts": "Max attempts",
        "retrying": "Retrying",
        "failed": "Failed",
        "succeeded": "Succeeded",
        "stopped": "Stopped",
        "waiting": "Waiting",
        "analyzing": "Analyzing",
        "import": "Import",
        "export": "Export",
        "burn": "Burn",
        "eject": "Eject",
        "refresh": "Refresh",
        "start": "Start",
        "cancel": "Cancel",
        "open_folder": "Open folder",
        "rename": "Rename",
        "serialize": "Serialize",
        "remove_serial": "Remove serialization",
        "choose": "Choose",
        "select": "Select",
        "confirm": "Confirm",
        "continue": "Continue",
        "back": "Back",
        "exit": "Exit",
        "help": "Help",
        "about": "About",
        "settings": "Settings",
        "language_settings": "Language settings",
        "appearance": "Appearance",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "system_default": "System default",
        "advanced": "Advanced",
        "basic": "Basic",
        "simple": "Simple",
        "expert": "Expert",
        "beginner": "Beginner",
        "user_interface": "User interface",
        "functionality": "Functionality",
        "performance": "Performance",
        "storage": "Storage",
        "usb_device": "USB device",
        "drive": "Drive",
        "partition": "Partition",
        "file_system": "File system",
        "auto_play": "Auto-play",
        "metadata": "Metadata",
        "id3_tags": "ID3 tags",
        "audio_properties": "Audio properties",
        "video_properties": "Video properties",
        "codec": "Codec",
        "bit_depth": "Bit depth",
        "sample_rate": "Sample rate",
        "frame_rate": "Frame rate",
        "resolution": "Resolution",
        "aspect_ratio": "Aspect ratio",
        "duration": "Duration",
        "file_size": "File size",
        "format": "Format",
        "container": "Container",
        "extension": "Extension",
        "filename": "Filename",
        "directory": "Directory",
        "path": "Path",
        "size": "Size",
        "date_modified": "Date modified",
        "date_created": "Date created",
        "attributes": "Attributes",
        "permissions": "Permissions",
        "owner": "Owner",
        "group": "Group",
        "hidden": "Hidden",
        "read_only": "Read only",
        "system_file": "System file",
        "archive": "Archive",
        "compressed": "Compressed",
        "encrypted": "Encrypted",
        "temporary": "Temporary",
        "offline": "Offline",
        "not_content_indexed": "Not content indexed",
        "integrity_stream": "Integrity stream",
        "no_scrub_data": "No scrub data",
        "virtual": "Virtual",
        "tab_download": "DOWNLOAD",
        "tab_randomize": "RANDOMIZING",
        "tab_burning": "USB BURNING",
        "file_list": "File List",
        "original_name": "Original Name",
        "new_name": "New Name",
        "loading_files": "Loading files...",
        "files_loaded": "Files loaded: {}",
        "renaming_files": "Renaming files...",
        "serialization_removed": "Serial numbers removed",
        "theme": "Theme",
        "donation_title": "Support Development",
        "donation_message": "Thank you for using our free software!\n\nIf you enjoy this program and would like to support further development, please consider making a donation. Every contribution, no matter how small, helps maintain and improve this tool.\n\nWould you like to visit our donation page?",
        "donation_yes": "Yes, I'd like to support",
        "donation_no": "No thanks",
        "donation_thanks": "Thank you for your support!",
        "tab_about": "ABOUT",
        "program_description": "Program Description",
        "about_description_left": "This YouTube Downloader allows you to:\n\n- Download videos or audio from YouTube\n- Process playlists and multiple links\n- Randomize and organize your music files\n- Create USB drives optimized for car audio systems",
        "about_features_right": "Features:\n✔ Supports multiple formats and quality settings\n✔ Batch processing of multiple files\n✔ Multi-language support\n✔ Clean and intuitive interface\n✔ Fast downloads with multiple threads\n✔ Error recovery and retry system\n✔ USB burning capabilities",
        "how_to_use": "How To Use",
        "usage_instructions_text": "1. DOWNLOAD TAB:\n   - Paste YouTube URL(s) in the input field\n   - Select download options (audio/video, format, quality)\n   - Choose destination folder\n   - Click DOWNLOAD button\n\n2. RANDOMIZE TAB:\n   - Select folder with your files\n   - Choose randomization method\n   - Click Randomize or Remove Serialization\n\n3. USB BURNING TAB:\n   - Select source folder with music\n   - Choose USB drive\n   - Click BURN TO USB",
        "developer_info": "Developer Information",
        "developer_info_text": "Created with ♡ by Emrah Ponjevic\n\nFind me on:\n GitHub: github.com/emrahponjevic\n• LinkedIn: linkedin.com/in/emrahponjevic\n\nFor support or feature requests:\n✉️ emrah.ponjevic@gmail.com",
        "support_project": "Support This Project",
        "donation_appeal_text": "If you find this software useful, please consider supporting its development.\nYour donation helps maintain and improve this tool.",
        "donate_now": "Donate Now",
        "GitHub": "GitHub",
        "LinkedIn": "LinkedIn",
        "version_info": "YouTube Downloader v1.0"
    },
    "Deutch": {
        "app_title": "YouTube Downloader by emrah-dev.net",
        "youtube_link": "YouTube-Link/Playlist (link einfügen):",
        "language": "Sprache:",
        "download": "💾 HERUNTERLADEN",
        "stop": "✋ STOPP",
        "error": "Fehler",
        "error_no_link": "Bitte gib einen gültigen YouTube-Link oder eine Playlist ein.",
        "error_no_folder": "Bitte wähle einen Speicherordner aus.",
        "status_waiting": "Status: Warte auf Eingabe...",
        "status_downloading": "Lade herunter... {percent:.0f}%",
        "status_finished": "Download abgeschlossen!",
        "status_start": "Starte Download...",
        "status_stopped": "Download gestoppt!",
        "options": "DOWNLOAD OPTIONEN",
        "media_audio": "Audio",
        "media_video": "Video",
        "format": "Format:",
        "bitrate": "Bitrate:",
        "resolution": "Auflösung:",
        "extra_options": "Zusatzoptionen",
        "normalize_audio": "Lautstärke normalisieren",
        "choose_folder": "Ordner wählen",
        "list_for_download": "DOWNLOAD LISTE",
        "randomize_section": "DATEIOPERATIONEN",
        "choose_folder_random": "Ordner wählen",
        "randomize_button": "Randomisieren und nummerieren",
        "remove_serial_button": "Nummerierung entfernen",
        "randomize_method": "Methode:",
        "alphabetical": "Alphabetisch",
        "by_artist": "Nach Künstler",
        "random": "Zufällig",
        "error_no_files": "Ordner ist leer.",
        "success_randomize": "Randomisierung und Nummerierung abgeschlossen!",
        "success_remove_serial": "Nummerierung entfernt!",
        "success_download": "Download abgeschlossen!",
        "success_message": "Möchten Sie den Download-Ordner öffnen?",
        "error_rename": "Kann {file} nicht umbenennen:\n{error}",
        "status_analyzing": "Links werden analysiert und importieren... (dies kann eine Weile dauern)",
        "column_no": "Nr.",
        "column_file": "Datei/URL",
        "column_status": "Status",
        "status_playlist_item": "Verarbeite Element {current}/{total}",
        "error_playlist_item": "Überspringe ungültiges Element",
        "error_video_format": "Video-Download-Fehler: {error}",
        "status_completed": "Abgeschlossen",
        "status_error": "Fehler",
        "converted_label": "Konvertiert: {}/{}",
        "status_converting": "Konvertierung...",
        "status_file_check": "Überprüfe Datei...",
        "file_check_failed": "Datei nicht gefunden: {}",
        "status_download_complete": "Download abgeschlossen",
        "import_label": "oder aus Datei importieren (.txt)",
        "import_button": "IMPORTIEREN AUS TXT",
        "import_success": "{} Links importiert",
        "import_error": "Importfehler",
        "import_empty": "Datei ist leer oder enthält keine gültigen Links",
        "usb_burning": "USB BURNING",
        "select_usb": "USB-Laufwerk auswählen:",
        "refresh": "Aktualisieren",
        "burn_usb": "🔥 AUF USB BRENNEN",
        "burning": "Brenne auf USB...",
        "burn_complete": "USB-Brennen abgeschlossen!",
        "ejecting": "Sicheres Auswerfen...",
        "usb_ejected": "USB Media ausgeworfen!",
        "confirm_burn": "Dadurch werden ALLE Daten auf {} gelöscht!\nSind Sie sicher, dass Sie fortfahren möchten?",
        "no_usb": "Keine USB-Laufwerke gefunden",
        "select_folder": "Bitte wählen Sie einen Ordner zum Brennen aus.",
        "choose_burn_folder": "Ordner wählen",
        "burn_folder": "Zu brennender Ordner:",
        "burn_progress": "Brennen: {copied}/{total} Dateien",
        "preparing_structure": "Bereite Auto-Play Struktur vor...",
        "creating_autoplay": "Erstelle Auto-Play-Dateien...",
        "writing_metadata": "Schreibe Titelinformationen...",
        "error_no_files": "Keine Musikdateien im Ordner gefunden",
        "error_metadata": "Metadaten konnten nicht geschrieben werden für: {}",
        "autorun_created": "Auto-Play für Autoradios konfiguriert!",
        "usb_ready": "USB ist für die Nutzung im Auto bereit!",
        "admin_format_required": "Administratorrechte für Formatierung erforderlich. Führen Sie die App als Administrator aus.",
        "error_file_empty": "FEHLER: Die heruntergeladene Datei ist leer! Video möglicherweise nicht verfügbar, privat oder urheberrechtlich geschützt.",
        "error_private_video": "FEHLER: Video ist privat oder wurde entfernt.",
        "error_geo_restricted": "FEHLER: Video in Ihrer Region nicht verfügbar.",
        "status_retrying": "Erneuter Versuch ({attempt}/{max_attempts})...",
        "status_failed_after_retries": "FEHLER: Nach {max_attempts} Versuchen fehlgeschlagen",
        "status_waiting_item": "Warten",
        "status_downloading_item": "Herunterladen",
        "status_converting_item": "Konvertieren",
        "status_completed_item": "Abgeschlossen",
        "status_error_item": "Fehler",
        "status_stopped_item": "Gestoppt",
        "invalid_item": "Ungültiges Element",
        "folder_empty": "Ordner ist leer",
        "usb_format_failed": "USB-Formatierung fehlgeschlagen",
        "usb_structure_failed": "Strukturerstellung fehlgeschlagen",
        "copy_failed": "Dateikopie fehlgeschlagen",
        "usb_eject_failed": "USB-Auswurf fehlgeschlagen",
        "usb_features": "Funktionen umfassen:\n- FAT32-Format für Kompatibilität\n- Auto-Play-Unterstützung\n- Verbesserte Metadaten\n- Organisierte Struktur\n- Master-Playlist",
        "admin_required": "Administratorrechte erforderlich",
        "processing_item": "Element wird verarbeitet",
        "video": "Video",
        "file_not_found": "Datei nicht gefunden",
        "invalid_url": "Ungültige URL",
        "starting_download": "Download startet",
        "downloading": "Wird heruntergeladen",
        "converting": "Wird konvertiert",
        "download_success": "Download erfolgreich",
        "download_failed": "Download fehlgeschlagen",
        "all_done": "Alles erledigt",
        "usb_not_found": "USB-Gerät nicht gefunden",
        "source_folder_error": "Quellordner-Fehler",
        "usb_selection_error": "USB-Auswahlfehler",
        "burning_started": "Brennen gestartet",
        "formatting": "Wird formatiert",
        "creating_structure": "Struktur wird erstellt",
        "copying_files": "Dateien werden kopiert",
        "enhancing_metadata": "Metadaten werden verbessert",
        "finalizing": "Wird finalisiert",
        "ejecting_usb": "USB wird ausgeworfen",
        "operation_complete": "Vorgang abgeschlossen",
        "file_operations": "Dateioperationen",
        "serialization": "Serialisierung",
        "deserialization": "Deserialisierung",
        "folder_selection": "Ordnerauswahl",
        "download_options": "Download-Optionen",
        "media_type": "Medientyp",
        "audio_format": "Audioformat",
        "video_format": "Videoformat",
        "quality_settings": "Qualitätseinstellungen",
        "normalization": "Normalisierung",
        "download_list": "Download-Liste",
        "progress": "Fortschritt",
        "conversion_status": "Konvertierungsstatus",
        "system_status": "Systemstatus",
        "actions": "Aktionen",
        "usb_operations": "USB-Operationen",
        "drive_selection": "Laufwerksauswahl",
        "burn_process": "Brennprozess",
        "file_management": "Dateiverwaltung",
        "sorting_method": "Sortiermethode",
        "randomization": "Randomisierung",
        "status": "Status",
        "item": "Element",
        "url": "URL",
        "no": "Nr.",
        "file": "Datei",
        "percent_complete": "Prozent abgeschlossen",
        "total_items": "Gesamte Elemente",
        "completed_items": "Abgeschlossene Elemente",
        "queue": "Warteschlange",
        "playlist": "Playlist",
        "single_video": "Einzelnes Video",
        "attempt": "Versuch",
        "max_attempts": "Maximale Versuche",
        "retrying": "Erneut versuchen",
        "failed": "Fehlgeschlagen",
        "succeeded": "Erfolgreich",
        "stopped": "Gestoppt",
        "waiting": "Warten",
        "analyzing": "Analysieren",
        "import": "Importieren",
        "export": "Exportieren",
        "burn": "Brennen",
        "eject": "Auswerfen",
        "refresh": "Aktualisieren",
        "start": "Starten",
        "cancel": "Abbrechen",
        "open_folder": "Ordner öffnen",
        "rename": "Umbenennen",
        "serialize": "Serialisieren",
        "remove_serial": "Serialisierung entfernen",
        "choose": "Auswählen",
        "select": "Auswählen",
        "confirm": "Bestätigen",
        "continue": "Fortsetzen",
        "back": "Zurück",
        "exit": "Beenden",
        "help": "Hilfe",
        "about": "Über",
        "settings": "Einstellungen",
        "language_settings": "Spracheinstellungen",
        "appearance": "Erscheinungsbild",
        "theme": "Thema",
        "light": "Hell",
        "dark": "Dunkel",
        "system_default": "Systemstandard",
        "advanced": "Fortgeschritten",
        "basic": "Basis",
        "simple": "Einfach",
        "expert": "Experte",
        "beginner": "Anfänger",
        "user_interface": "Korisničko sučelje",
        "functionality": "Funktionalität",
        "performance": "Leistung",
        "storage": "Speicher",
        "usb_device": "USB-Gerät",
        "drive": "Laufwerk",
        "partition": "Partition",
        "file_system": "Dateisystem",
        "auto_play": "Auto-Play",
        "metadata": "Metadaten",
        "id3_tags": "ID3-Tags",
        "audio_properties": "Audioeigenschaften",
        "video_properties": "Videoeigenschaften",
        "codec": "Codec",
        "bit_depth": "Bittiefe",
        "sample_rate": "Samplerate",
        "frame_rate": "Bildrate",
        "resolution": "Auflösung",
        "aspect_ratio": "Seitenverhältnis",
        "duration": "Dauer",
        "file_size": "Dateigröße",
        "format": "Format",
        "container": "Container",
        "extension": "Erweiterung",
        "filename": "Dateiname",
        "directory": "Verzeichnis",
        "path": "Pfad",
        "size": "Größe",
        "date_modified": "Geändert am",
        "date_created": "Erstellt am",
        "attributes": "Attribute",
        "permissions": "Berechtigungen",
        "owner": "Besitzer",
        "group": "Gruppe",
        "hidden": "Versteckt",
        "read_only": "Nur Lesen",
        "system_file": "Systemdatei",
        "archive": "Archiv",
        "compressed": "Komprimiert",
        "encrypted": "Verschlüsselt",
        "temporary": "Temporär",
        "offline": "Offline",
        "not_content_indexed": "Nicht indiziert",
        "integrity_stream": "Integritätsstrom",
        "no_scrub_data": "Keine Bereinigungsdaten",
        "virtual": "Virtuell",
        "tab_download": "HERUNTERLADEN",
        "tab_randomize": "RANDOMISIERUNG",
        "tab_burning": "USB BRENNEN",
        "file_list": "Dateiliste",
        "original_name": "Originalname",
        "new_name": "Neuer Name",
        "loading_files": "Lade Dateien...",
        "files_loaded": "Dateien geladen: {}",
        "renaming_files": "Benenne Dateien um...",
        "serialization_removed": "Seriennummern entfernt",
        "theme": "Thema",
        "donation_title": "Unterstützung",
        "donation_message": "Vielen Dank für die Nutzung unserer kostenlosen Software!\n\nWenn Ihnen dieses Programm gefällt und Sie die weitere Entwicklung unterstützen möchten, erwägen Sie bitte eine Spende. Jeder Beitrag, egal wie klein, hilft bei der Wartung und Verbesserung dieses Tools.\n\nMöchten Sie unsere Spendenseite besuchen?",
        "donation_yes": "Ja, ich möchte unterstützen",
        "donation_no": "Nein danke",
        "donation_thanks": "Vielen Dank für Ihre Unterstützung!",
        "tab_about": "ÜBER",
        "program_description": "Programmbeschreibung",
        "about_description_left": "Dieser YouTube Downloader ermöglicht Ihnen:\n\n- Videos oder Audio von YouTube herunterzuladen\n- Playlists und mehrere Links zu verarbeiten\n- Musikdateien zu randomisieren und zu organisieren\n- USB-Laufwerke für Auto-Audiosysteme zu optimieren",
        "about_features_right": "Funktionen:\n✔ Unterstützt mehrere Formate und Qualitätseinstellungen\n✔ Stapelverarbeitung mehrerer Dateien\n✔ Mehrsprachige Unterstützung\n✔ Saubere und intuitive Oberfläche\n✔ Schnelle Downloads mit mehreren Threads\n✔ Fehlerwiederherstellung und Wiederholungssystem\n✔ USB-Brennfähigkeiten",
        "how_to_use": "Anleitung",
        "usage_instructions_text": "1. DOWNLOAD TAB:\n   - YouTube-URL(s) in das Eingabefeld einfügen\n   - Download-Optionen auswählen (Audio/Video, Format, Qualität)\n   - Zielordner auswählen\n   - DOWNLOAD-Button klicken\n\n2. RANDOMISIERUNG TAB:\n   - Ordner mit Ihren Dateien auswählen\n   - Randomisierungsmethode auswählen\n   - Randomisieren oder Nummerierung entfernen klicken\n\n3. USB BRENNEN TAB:\n   - Quellordner mit Musik auswählen\n   - USB-Laufwerk auswählen\n   - AUF USB BRENNEN klicken",
        "developer_info": "Entwicklerinformation",
        "developer_info_text": "Erstellt mit ♡ von Emrah Ponjevic\n\nFinden Sie mich auf:\n GitHub: github.com/emrahponjevic\n• LinkedIn: linkedin.com/in/emrahponjevic\n\nFür Support oder Funktionsanfragen:\n✉️ emrah.ponjevic@gmail.com",
        "support_project": "Projekt unterstützen",
        "donation_appeal_text": "Wenn Sie diese Software nützlich finden, erwägen Sie bitte eine Unterstützung der Entwicklung.\nIhre Spende hilft bei der Wartung und Verbesserung dieses Tools.",
        "donate_now": "Jetzt spenden",
        "GitHub": "GitHub",
        "LinkedIn": "LinkedIn",
        "version_info": "YouTube Downloader v1.0"
}}

def tr(key):
    default_lang = "English"  # Changed default to English
    lang = default_lang
    try:
        lang = language_combo.get()
    except:
        pass
    return translations.get(lang, translations["English"]).get(key, key)

# --- Constants ---
MAX_DOWNLOAD_ATTEMPTS = 2
DONATION_URL = "https://paypal.me/emrahponjevic"  # Replace with your actual donation link

# --- Global variables for USB progress ---
current_usb_copied = 0
current_usb_total = 0
last_usb_status_key = None
last_usb_status_args = None

# --- Functions for file operations ---
def choose_random_folder():
    folder = filedialog.askdirectory()
    if folder:
        random_folder_var.set(folder)
        populate_file_list(folder)

def populate_file_list(folder):
    original_listbox.delete(0, tk.END)
    new_listbox.delete(0, tk.END)
    file_status_var.set(tr("loading_files"))
    
    try:
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        if not files:
            file_status_var.set(tr("folder_empty"))
            return
            
        for filename in files:
            original_listbox.insert(tk.END, filename)
            new_listbox.insert(tk.END, "")
            
        file_status_var.set(tr("files_loaded").format(len(files)))
    except Exception as e:
        file_status_var.set(f"{tr('error')}: {str(e)}")

def extract_artist(filename):
    """Extract artist name from filename with fallbacks"""
    # Remove existing serial number pattern if present
    base = re.sub(r"^\d{3,4}\s*-\s*", "", filename)
    # Remove file extension
    base = os.path.splitext(base)[0]
    
    # Try common patterns
    patterns = [
        r"(.+?)\s*-\s*(.+)",  # Artist - Title
        r"(.+?)\s*–\s*(.+)",  # Artist – Title (with en dash)
        r"(.+?)\s*_\s*(.+)",  # Artist_Title
        r"(.+?)\s*\.\s*(.+)", # Artist.Title
    ]
    
    for pattern in patterns:
        match = re.match(pattern, base)
        if match:
            return match.group(1).strip()
    
    # Fallback if no pattern matches
    return "Unknown"

def shuffle_with_artist_distribution(files):
    """Advanced shuffling with artist separation"""
    # Group files by artist
    artist_groups = defaultdict(list)
    for filename in files:
        artist = extract_artist(filename)
        artist_groups[artist].append(filename)
    
    # Shuffle songs within each artist group
    for group in artist_groups.values():
        random.shuffle(group)
    
    # Sort groups by size (largest first)
    sorted_groups = sorted(artist_groups.values(), key=len, reverse=True)
    
    # Create distributed list using round-robin with jitter
    result = []
    max_len = max(len(group) for group in sorted_groups) if sorted_groups else 0
    
    for i in range(max_len):
        # Add randomness to the group order each round
        random.shuffle(sorted_groups)
        for group in sorted_groups:
            if i < len(group):
                result.append(group[i])
    
    return result

def randomize_files():
    folder = random_folder_var.get()
    if not folder or not os.path.isdir(folder):
        messagebox.showerror(tr("error"), tr("error_no_folder"))
        return
        
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        messagebox.showerror(tr("error"), tr("folder_empty"))
        return
        
    file_status_var.set(tr("renaming_files"))
    method = randomize_method.get()
    
    if method == "alphabetical":
        files.sort()
    elif method == "by_artist":
        # Sort by artist then by title
        files.sort(key=lambda f: (extract_artist(f), f))
    elif method == "random":
        # Use advanced shuffling algorithm
        files = shuffle_with_artist_distribution(files)
    else:
        files = shuffle_with_artist_distribution(files)

    original_listbox.delete(0, tk.END)
    new_listbox.delete(0, tk.END)
    
    for i, filename in enumerate(files, 1):
        old_path = os.path.join(folder, filename)
        new_name = f"{i:03d} - {filename}"
        new_path = os.path.join(folder, new_name)
        
        original_listbox.insert(tk.END, filename)
        new_listbox.insert(tk.END, new_name)
        
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            messagebox.showerror(tr("error"), tr("error_rename").format(file=filename, error=str(e)))
            file_status_var.set(tr("error"))
            return
            
    file_status_var.set(tr("success_randomize"))
    messagebox.showinfo(tr("success_randomize"), tr("success_randomize"))

def remove_serial():
    folder = random_folder_var.get()
    if not folder or not os.path.isdir(folder):
        messagebox.showerror(tr("error"), tr("error_no_folder"))
        return
        
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    
    original_listbox.delete(0, tk.END)
    new_listbox.delete(0, tk.END)
    
    for filename in files:
        new_name = re.sub(r"^\d{3,4}\s*-\s*", "", filename)
        if new_name != filename:
            old_path = os.path.join(folder, filename)
            new_path = os.path.join(folder, new_name)
            
            original_listbox.insert(tk.END, filename)
            new_listbox.insert(tk.END, new_name)
            
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                messagebox.showerror(tr("error"), tr("error_rename").format(file=filename, error=str(e)))
                file_status_var.set(tr("error"))
                return
                
    file_status_var.set(tr("serialization_removed"))
    messagebox.showinfo(tr("success_remove_serial"), tr("success_remove_serial"))

# --- Import function ---
def import_from_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not file_path:
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            links = file.readlines()
        
        valid_links = []
        for link in links:
            link = link.strip()
            if link and ("youtube.com" in link or "youtu.be" in link):
                valid_links.append(link)
        
        if not valid_links:
            messagebox.showerror(tr("import_error"), tr("import_empty"))
            return
            
        link_entry.delete(0, tk.END)
        link_entry.insert(0, "\n".join(valid_links))
        messagebox.showinfo(tr("import_success"), tr("import_success").format(len(valid_links)))
        
    except Exception as e:
        messagebox.showerror(tr("import_error"), f"{tr('import_error')}: {str(e)}")

# --- Dependency Check ---
usb_dependencies_available = True
try:
    import psutil
    try:
        from PIL import Image, ImageDraw
        import eyed3
    except ImportError:
        usb_dependencies_available = False
except ImportError:
    usb_dependencies_available = False

# --- USB Burning Functions ---
if usb_dependencies_available:
# Unutar `if usb_dependencies_available:` bloka...

    def is_fat32(drive_path):
        """
        Poboljšana provjera za FAT32. Pokušava više puta ako je potrebno,
        da bi se riješio problem sa "timingom" nakon formatiranja.
        """
        drive_letter = drive_path.strip(":\\")
        # Pokušaj do 5 puta (ukupno 5 sekundi)
        for attempt in range(5):
            try:
                if os.name == 'nt':
                    print(f"Checking FAT32 on {drive_letter}: (Attempt {attempt + 1})")
                    creation_flags = subprocess.CREATE_NO_WINDOW
                    result = subprocess.run(
                        f'fsutil fsinfo volumeinfo {drive_letter}:',
                        shell=True, capture_output=True, text=True, creationflags=creation_flags, timeout=5
                    )
                    
                    # Provjeravamo izlaz. Ako diskpart uspije, izlaz mora sadržavati "FAT32".
                    if result.returncode == 0 and "FAT32" in result.stdout.upper():
                        print("FAT32 confirmed.")
                        return True
                    else:
                        print(f"Attempt {attempt + 1} failed. stdout: {result.stdout.strip()}, stderr: {result.stderr.strip()}")
                
                else: # posix logika
                    result = subprocess.run(["df", "-T", drive_path], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and len(result.stdout.splitlines()) > 1:
                        if 'vfat' in result.stdout.splitlines()[1].lower():
                            return True
                
                # Ako provjera nije uspjela, čekaj sekundu prije novog pokušaja
                time.sleep(1)

            except (subprocess.TimeoutExpired, Exception) as e:
                print(f"Exception in is_fat32 on attempt {attempt + 1}: {e}")
                time.sleep(1) # Čekaj i u slučaju greške

        # Ako nakon svih pokušaja nije uspjelo, vrati False
        print(f"Could not confirm FAT32 on {drive_letter}: after multiple attempts.")
        return False

    def format_fat32(drive_path):
        """
        Poboljšana funkcija za formatiranje koja šalje detaljne statuse za GUI.
        """
        try:
            if os.name != 'nt':
                usb_queue.put(("error", "USB formatting is currently supported on Windows only."))
                return False

            drive_letter = drive_path.strip(":\\")
            
            # --- NOVI KORACI ZA GUI ---
            # 1. Početni status
            usb_queue.put(("status", "1/5: Starting format..."))
            usb_queue.put(("progress_bar", 10)) # Postavi progress bar na 10%
            print("1/5: Starting format...")

            # 2. Demontiranje
            usb_queue.put(("status", "2/5: Releasing drive locks..."))
            usb_queue.put(("progress_bar", 25)) # 25%
            try:
                print("Attempting to dismount volume...")
                subprocess.run(
                    f"fsutil volume dismount {drive_letter}:",
                    shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                time.sleep(2)
            except Exception as e:
                print(f"Could not dismount volume (this is often OK). Error: {e}")

            # 3. Izvršavanje diskpart-a
            usb_queue.put(("status", "3/5: Formatting drive (this may take a moment)..."))
            usb_queue.put(("progress_bar", 50)) # 50%
            
            script = f"""
            select volume {drive_letter}
            clean
            create partition primary
            select partition 1
            active
            format fs=fat32 quick label="CAR_MUSIC"
            assign letter={drive_letter}
            exit
            """
            script_path = os.path.join(os.getcwd(), "format_script.txt")
            with open(script_path, "w") as f:
                f.write(script)
            
            print("Executing diskpart script...")
            try:
                subprocess.run(
                    f'diskpart /s "{script_path}"',
                    shell=True, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
            except subprocess.CalledProcessError as e:
                print(f"--- DISKPART FAILED! ---\nError: {e.stderr}\nOutput: {e.stdout}")
                usb_queue.put(("error", tr("usb_format_failed") + f":\n{e.stderr.strip()}"))
                return False
            finally:
                if os.path.exists(script_path):
                    os.remove(script_path)

            # 4. Čekanje da se disk pojavi
            usb_queue.put(("status", "4/5: Re-initializing drive..."))
            usb_queue.put(("progress_bar", 75)) # 75%
            print("Waiting for drive to become available...")
            drive_ready = False
            for i in range(20):
                if os.path.exists(f"{drive_letter}:\\"):
                    drive_ready = True
                    break
                time.sleep(1)
            
            if not drive_ready:
                usb_queue.put(("error", tr("usb_format_failed")))
                return False
            
            time.sleep(2)

            # 5. Finalna provjera
            usb_queue.put(("status", "5/5: Verifying format..."))
            usb_queue.put(("progress_bar", 90)) # 90%
            if is_fat32(f"{drive_letter}:\\"):
                print("--- FORMATTING SUCCEEDED! ---")
                usb_queue.put(("progress_bar", 100)) # 100%
                return True
            else:
                print("--- FORMATTING FAILED! (is_fat32 check failed) ---")
                usb_queue.put(("error", tr("usb_format_failed")))
                return False

        except Exception as e:
            print(f"An unexpected exception occurred in format_fat32: {str(e)}")
            usb_queue.put(("error", tr("usb_format_failed")))
            return False

    def create_car_friendly_structure(dest_path, source_folder):
        """Kreiranje strukture foldera, AUTORUN.INF i glavne playliste."""
        try:
            usb_queue.put(("status", tr("creating_structure")))
            music_dir = os.path.join(dest_path, "MUSIC")
            playlists_dir = os.path.join(dest_path, "PLAYLISTS")
            os.makedirs(music_dir, exist_ok=True)
            os.makedirs(playlists_dir, exist_ok=True)

            # AUTORUN.INF za starije uređaje i ljepšu ikonicu/labelu
            autorun_path = os.path.join(dest_path, "AUTORUN.INF")
            with open(autorun_path, "w") as f:
                f.write(f"[autorun]\n")
                f.write(f"label=CAR_MUSIC\n")
                f.write(f"icon=autorun.ico\n")
            
            # Kreiraj ikonicu
            create_radio_icon(os.path.join(dest_path, "autorun.ico"))
            
            # Kreiraj glavnu M3U playlistu
            create_main_playlist(dest_path, source_folder)
            
            usb_queue.put(("status", tr("autorun_created")))
            return True
        except Exception as e:
            print(f"Error creating structure: {e}")
            usb_queue.put(("error", tr("usb_structure_failed")))
            return False

    def create_main_playlist(dest_path, source_folder):
        """Kreiranje .m3u playliste svih pjesama."""
        playlist_path = os.path.join(dest_path, "PLAYLISTS", "00_ALL_SONGS.m3u")
        music_files = []
        for root, _, files in os.walk(os.path.join(dest_path, "MUSIC")):
            for file in sorted(files):
                if file.lower().endswith(('.mp3', '.m4a', '.flac', '.wav')):
                    # Putanja relativna u odnosu na playlistu
                    relative_path = os.path.join("..", "MUSIC", os.path.basename(file))
                    music_files.append(relative_path.replace("\\", "/"))

        if not music_files: return
        
        with open(playlist_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n\n")
            for file_path in music_files:
                title = os.path.splitext(os.path.basename(file_path))[0]
                f.write(f"#EXTINF:-1,{title}\n")
                f.write(f"{file_path}\n\n")

    def create_radio_icon(icon_path):
        """Kreiranje jednostavne .ico datoteke."""
        try:
            img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # Jednostavan dizajn note
            draw.ellipse((8, 2, 22, 16), fill='dodgerblue', outline='black')
            draw.line((22, 9, 22, 28), fill='black', width=3)
            draw.line((14, 28, 22, 28), fill='black', width=3)
            img.save(icon_path, format='ICO', sizes=[(16,16), (24,24), (32, 32)])
        except Exception as e:
            print(f"Could not create icon: {e}")

    def enhance_metadata(file_path):
        """Dodavanje osnovnih ID3 tagova ako ne postoje."""
        if not file_path.lower().endswith(".mp3"): return
        try:
            audio = eyed3.load(file_path)
            if audio is None: return # Preskoči ako eyed3 ne može pročitati fajl
            
            if audio.tag is None:
                audio.initTag()
            
            # Ako su tagovi prazni, popuni ih iz imena fajla
            if not audio.tag.title:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                # Ukloni serijski broj ako postoji
                cleaned_name = re.sub(r"^\d{3,4}\s*-\s*", "", base_name)
                
                if " - " in cleaned_name:
                    artist, title = cleaned_name.split(" - ", 1)
                    audio.tag.artist = artist.strip()
                    audio.tag.title = title.strip()
                else:
                    audio.tag.title = cleaned_name
            
            audio.tag.save(version=eyed3.id3.ID3_V2_3)
        except Exception as e:
            print(f"Could not enhance metadata for {os.path.basename(file_path)}: {e}")

    def copy_with_progress(src, dest):
        """Kopiranje fajlova sa prikazom progresa i poboljšanjem metapodataka."""
        music_dest = os.path.join(dest, "MUSIC")
        all_files = [os.path.join(root, file) for root, _, files in os.walk(src) for file in files if file.lower().endswith(('.mp3', '.m4a', '.flac', '.wav'))]
        
        total_files = len(all_files)
        if total_files == 0:
            usb_queue.put(("error", tr("error_no_files")))
            return False
            
        usb_queue.put(("status", tr("copying_files")))
        for i, file_path in enumerate(all_files):
            try:
                dest_path = os.path.join(music_dest, os.path.basename(file_path))
                shutil.copy2(file_path, dest_path)
                enhance_metadata(dest_path) # Poboljšaj metapodatke nakon kopiranja
                usb_queue.put(("progress", i + 1, total_files, int(((i + 1) / total_files) * 100)))
            except Exception as e:
                print(f"Failed to copy {os.path.basename(file_path)}: {e}")
        return True

    def eject_drive(drive_path):
        """Pouzdano izbacivanje drajva koristeći PowerShell."""
        usb_queue.put(("status", tr("ejecting")))
        try:
            if os.name == 'nt':
                drive_letter = drive_path.strip(":\\")
                ps_command = f"""
                $driveEject = New-Object -comObject Shell.Application;
                $driveEject.Namespace(17).ParseName('{drive_letter}:').InvokeVerb("Eject")
                """
                subprocess.run(["powershell", "-Command", ps_command], check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                print(f"Eject command sent to drive {drive_letter}:")
                return True
            else: # posix
                subprocess.run(["eject", drive_path], check=True)
                return True
        except Exception as e:
            print(f"Eject drive failed: {e}")
            usb_queue.put(("error", tr("usb_eject_failed")))
            return False

    def burn_to_usb_thread(source_folder, usb_path):
        """Glavni thread za kompletan proces."""
        try:
            # Onemogući gumbe na početku
            usb_queue.put(("disable_buttons",))
            
            if not format_fat32(usb_path):
                # Poruka o grešci je već poslana iz format_fat32
                return
            
            # Pauza da budemo sigurni da je OS spreman za upisivanje
            time.sleep(3)
            
            if not create_car_friendly_structure(usb_path, source_folder):
                return
            
            if not copy_with_progress(source_folder, usb_path):
                return

            usb_queue.put(("success", tr("usb_ready")))
            
            # Pokušaj izbacivanja na kraju
            time.sleep(1)
            eject_drive(usb_path)

        except Exception as e:
            usb_queue.put(("error", f"{tr('error')}: {str(e)}"))
        finally:
            # UVIJEK omogući gumbe na kraju, bez obzira na ishod
            usb_queue.put(("enable_buttons",))

    def burn_to_usb():
        """Pokreće proces burninga u novom threadu."""
        source_folder = burn_folder_var.get()
        if not source_folder or not os.path.isdir(source_folder):
            messagebox.showerror(tr("error"), tr("source_folder_error"))
            return
        
        drives = refresh_usb_drives()
        if not drives or usb_combo.get() == tr("no_usb"):
            messagebox.showerror(tr("error"), tr("no_usb"))
            return
        
        selected_label = usb_combo.get()
        usb_path = next((path for path, label in drives if label == selected_label), None)
        if not usb_path:
            messagebox.showerror(tr("error"), tr("usb_selection_error"))
            return
        
        if not messagebox.askyesno(tr("confirm"), tr("confirm_burn").format(selected_label)):
            return
        
        threading.Thread(target=burn_to_usb_thread, args=(source_folder, usb_path), daemon=True).start()

    def refresh_usb_drives():
        """Osvježava listu dostupnih USB drajvova."""
        drives = []
        try:
            for p in psutil.disk_partitions(all=False):
                if 'removable' in p.opts:
                    try:
                        usage = psutil.disk_usage(p.mountpoint)
                        label = f"{p.mountpoint} ({usage.total / (1024**3):.1f}GB)"
                        drives.append((p.mountpoint, label))
                    except (PermissionError, FileNotFoundError):
                        continue
        except Exception as e:
            print(f"Error refreshing drives: {e}")
        
        if not drives:
            usb_combo['values'] = [tr("no_usb")]
            usb_combo.set(tr("no_usb"))
        else:
            usb_combo['values'] = [label for _, label in drives]
            usb_combo.current(0)
        return drives

else:
    # Fallback funkcije ako zavisnosti nisu instalirane
    def burn_to_usb():
        messagebox.showerror(tr("error"), "USB burning requires additional dependencies (psutil, Pillow, eyed3).")
    
    def refresh_usb_drives():
        usb_combo['values'] = [tr("no_usb")]
        usb_combo.set(tr("no_usb"))
        return []
# --- USB Progress Display ---
def update_usb_progress_display():
    usb_progress_text.set(
        tr("burn_progress").format(copied=current_usb_copied, total=current_usb_total)
    )
# --- Theme Functions ---
def update_theme():
    selected_theme = theme_combo.get()
    style.theme_use(selected_theme)
    
    style.configure("Accent.TButton", 
                   background=style.colors.primary, 
                   foreground="white",
                   font=("Segoe UI", 12, "bold"))
    
    style.configure("Stop.TButton", 
                   background=style.colors.danger, 
                   foreground="white",
                   font=("Segoe UI", 12, "bold"))
    
    style.configure("Progress.Horizontal.TProgressbar",
                   troughcolor=style.colors.bg,
                   bordercolor=style.colors.border,
                   lightcolor=style.colors.primary,
                   darkcolor=style.colors.primary)
    
    if 'original_listbox' in globals():
        bg_color = style.colors.inputbg if 'inputbg' in style.colors else style.colors.bg
        fg_color = style.colors.inputfg if 'inputfg' in style.colors else style.colors.fg
        sel_bg = style.colors.selectbg if 'selectbg' in style.colors else '#e6e6e6'
        sel_fg = style.colors.selectfg if 'selectfg' in style.colors else 'black'
        
        original_listbox.config(bg=bg_color, fg='red', selectbackground=sel_bg, selectforeground=sel_fg)
        new_listbox.config(bg=bg_color, fg='green', selectbackground=sel_bg, selectforeground=sel_fg)
    
    update_ui_texts()

# --- Donation Functions ---
def show_donation_popup():
    response = messagebox.askyesno(
        tr("donation_title"),
        tr("donation_message"),
        icon='question',
        default='no',
        parent=root
    )
    
    if response:
        try:
            webbrowser.open(DONATION_URL)
            messagebox.showinfo(tr("donation_title"), tr("donation_thanks"))
        except:
            messagebox.showerror(tr("error"), "Could not open donation page")

def on_close():
    show_donation_popup()
    root.destroy()

# --- UI Setup ---
style = Style("flatly")
root = style.master
root.title(tr("app_title"))
root.geometry("1000x900")
root.minsize(1000, 1000)
root.resizable(True, True)
try:
    # For Windows title bar icon
    root.iconbitmap(resource_path('logo.ico'))
    
    # For Linux/macOS and taskbar icon (optional)
    # Koristimo tk.PhotoImage i osiguravamo da je 'tk' importovan kao tkinter
    logo_img = tk.PhotoImage(file=resource_path('logo.gif'))
    root.iconphoto(False, logo_img)
except Exception as e:
    print(f"Could not load icons: {e}")

# Set close handler
root.protocol("WM_DELETE_WINDOW", on_close)

# Configure styles
style.configure("TFrame", background="#FFFFFF")
style.configure("TLabel", background="#FFFFFF", foreground="#212121")
style.configure("TButton", font=("Segoe UI", 12))
style.configure("Accent.TButton", background="#E50914", foreground="white",
                font=("Segoe UI", 12, "bold"))
style.configure("Stop.TButton", background="#FF6B6B", foreground="white",
                font=("Segoe UI", 12, "bold"))
style.configure("Card.TFrame", background="#FFFFFF", borderwidth=1, relief="solid")
style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))
style.configure("Progress.Horizontal.TProgressbar",
                troughcolor="#FFFFFF",
                bordercolor="#DDDDDD",
                lightcolor="#E50914",
                darkcolor="#E50914")
style.configure("Big.TButton", font=("Segoe UI", 12, "bold"), padding=10)

# Set tab width to 25% (for 4 tabs)
style.configure("TNotebook.Tab", width=1000/4, padding=[10, 5])

# --- Header frame ---
header_frame = ttk.Frame(root, padding=(15, 10))
header_frame.pack(fill=X, padx=10, pady=5)

# LEFT: Logo and title
left_frame = ttk.Frame(header_frame)
left_frame.pack(side=LEFT, fill=X, expand=True)

# Load and resize GIF logo with fallback to text
try:
    # Load original GIF
    original_logo = tk.PhotoImage(file=resource_path("logo.gif"))  # Replace with your GIF filename
    
    # Calculate new size (adjust these values as needed)
    new_width = 40  # Set your desired width
    new_height = 40  # Set your desired height
    
    # Create blank image of desired size
    resized_logo = tk.PhotoImage(width=new_width, height=new_height)
    
    # Copy and scale original image
    resized_logo = original_logo.subsample(
        max(1, original_logo.width() // new_width),
        max(1, original_logo.height() // new_height))
    
    logo = ttk.Label(left_frame, image=resized_logo)
    logo.image = resized_logo  # Keep reference
except Exception as e:
    print(f"Logo loading error: {e}")  # Optional debug message
    logo = ttk.Label(left_frame, text="▶️", font=("Segoe UI", 20))  # Fallback

logo.pack(side=LEFT, padx=(0, 10))

title_label = ttk.Label(left_frame, text=tr("app_title"), font=("Segoe UI", 16, "bold"))
title_label.pack(side=LEFT)

# RIGHT: Language and Theme selection
right_frame = ttk.Frame(header_frame)
right_frame.pack(side=RIGHT)

# Theme selection
theme_frame = ttk.Frame(right_frame)
theme_frame.pack(side=RIGHT, padx=(15, 0))

theme_label = ttk.Label(theme_frame, text=tr("theme") + ":")
theme_label.pack(side=LEFT, padx=(0, 5))

theme_combo = ttk.Combobox(theme_frame, values=AVAILABLE_THEMES, 
                           state="readonly", width=15)
theme_combo.current(0)
theme_combo.pack(side=LEFT)
theme_combo.bind("<<ComboboxSelected>>", lambda e: update_theme())
theme_frame.pack_forget()
# Language selection
language_frame = ttk.Frame(right_frame)
language_frame.pack(side=RIGHT, padx=(0, 15))

language_label = ttk.Label(language_frame, text=tr("language"))
language_label.pack(side=LEFT, padx=(0, 5))

language_combo = ttk.Combobox(language_frame, values=list(translations.keys()), 
                             state="readonly", width=15)
language_combo.current(1)  # Set to English by default
language_combo.pack(side=LEFT)

# --- Tab Control ---
tab_control = ttk.Notebook(root)
tab_control.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

# --- DOWNLOAD TAB ---
download_tab = ttk.Frame(tab_control)
tab_control.add(download_tab, text=tr("tab_download"))

# URL input section
url_frame = ttk.Frame(download_tab, style="Card.TFrame", padding=15)
url_frame.pack(fill=X, padx=15, pady=10)

link_label = ttk.Label(url_frame, text=tr("youtube_link"), font=("Segoe UI", 12))
link_label.pack(anchor="w", pady=(0, 5))

link_entry = ttk.Entry(url_frame)
link_entry.pack(fill=X, padx=0, pady=(0, 5), ipady=3)

separator = ttk.Separator(url_frame, orient="horizontal")
separator.pack(fill=X, pady=15)

# Import row
import_row = ttk.Frame(url_frame)
import_row.pack(fill=X, pady=(5, 0))

import_label = ttk.Label(import_row, text=tr("import_label"), font=("Segoe UI", 10))
import_label.pack(side=LEFT, padx=(0, 10))

import_button = ttk.Button(
    import_row, 
    text=tr("import_button"), 
    command=import_from_file,
    style="Accent.TButton",
)
import_button.pack(side=RIGHT)

# Download options section
options_frame = ttk.LabelFrame(download_tab, text=tr("options"), style="Card.TFrame", padding=15)
options_frame.pack(fill=X, padx=15, pady=10)

options_row = ttk.Frame(options_frame)
options_row.pack(fill=X)

# Media type selection
media_type = tk.StringVar(value="audio")
audio_radio = ttk.Radiobutton(options_row, text=tr("media_audio"), variable=media_type, 
                             value="audio")
audio_radio.pack(side=LEFT, padx=10)

video_radio = ttk.Radiobutton(options_row, text=tr("media_video"), variable=media_type, 
                             value="video")
video_radio.pack(side=LEFT, padx=10)

# Add separator
ttk.Separator(options_row, orient="vertical").pack(side=LEFT, padx=10, fill='y')

# Format selection
format_frame = ttk.Frame(options_row)
format_frame.pack(side=LEFT, padx=10, pady=5)

format_label = ttk.Label(format_frame, text=tr("format"))
format_label.grid(row=0, column=0, sticky="w")

format_combo = ttk.Combobox(format_frame, state="readonly", width=10)
format_combo.grid(row=1, column=0)

# Bitrate selection
bitrate_frame = ttk.Frame(options_row)
bitrate_frame.pack(side=LEFT, padx=10, pady=5)

bitrate_label = ttk.Label(bitrate_frame, text=tr("bitrate"))
bitrate_label.grid(row=0, column=0, sticky="w")

bitrate_combo = ttk.Combobox(bitrate_frame, state="readonly", 
                            values=["128 kbps", "192 kbps", "256 kbps", "320 kbps"], width=8)
bitrate_combo.grid(row=1, column=0)

# Resolution selection
resolution_frame = ttk.Frame(options_row)
resolution_frame.pack(side=LEFT, padx=10, pady=5)

resolution_label = ttk.Label(resolution_frame, text=tr("resolution"))
resolution_label.grid(row=0, column=0, sticky="w")

resolution_combo = ttk.Combobox(resolution_frame, state="readonly", 
                              values=["4320p (8K)", "2160p (4K)", "1440p (2K)", "1080p (HD)", 
                                      "720p (HD)", "480p (SD)", "360p (SD)", "240p (SD)"], 
                              width=12)
resolution_combo.current(3)
resolution_combo.grid(row=1, column=0)

# Normalize checkbox
normalize_frame = ttk.Frame(options_row)
normalize_frame.pack(side=RIGHT, padx=10, pady=5)

normalize_var = tk.BooleanVar()
normalize_check = ttk.Checkbutton(normalize_frame, text=tr("normalize_audio"), 
                                variable=normalize_var)
normalize_check.pack()

def update_format_options():
    if media_type.get() == "audio":
        format_combo["values"] = [".mp3", ".aac", ".m4a", ".flac", ".opus", ".wav"]
        format_combo.current(0)
        bitrate_frame.pack(side=LEFT, padx=10)
        resolution_frame.pack_forget()
        bitrate_combo.current(2)
    else:
        format_combo["values"] = [".mp4", ".mkv", ".webm", ".avi"]
        format_combo.current(0)
        resolution_frame.pack(side=LEFT, padx=10)
        bitrate_frame.pack_forget()

update_format_options()

media_type.trace_add("write", lambda *args: update_format_options())

# Folder selection section
folder_frame = ttk.Frame(download_tab, style="Card.TFrame", padding=15)
folder_frame.pack(fill=X, padx=15, pady=10)

save_path_var = tk.StringVar(value=tr("error_no_folder"))
folder_label = ttk.Label(folder_frame, textvariable=save_path_var, font=("Segoe UI", 12))
folder_label.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        save_path_var.set(folder)
folder_button = ttk.Button(folder_frame, text=tr("choose_folder"), 
                          command=choose_folder, style="Accent.TButton")
folder_button.pack(side=RIGHT)

# Download list section
list_frame = ttk.LabelFrame(download_tab, text=tr("list_for_download"), style="Card.TFrame", padding=10)
list_frame.pack(fill=BOTH, expand=True, padx=15, pady=10)

columns = ("no", "file", "status")
tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
tree.heading("no", text=tr("column_no"), anchor="w")
tree.heading("file", text=tr("column_file"), anchor="w")
tree.heading("status", text=tr("column_status"), anchor="w")
tree.column("no", width=40, anchor="w")
tree.column("file", width=500, anchor="w")
tree.column("status", width=150, anchor="w")
tree.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side=RIGHT, fill=Y)
tree.configure(yscrollcommand=scrollbar.set)

# Progress bar and status section
progress_status_frame = ttk.Frame(download_tab)
progress_status_frame.pack(fill=X, padx=15, pady=(5, 0))

progress_frame = ttk.Frame(progress_status_frame)
progress_frame.pack(fill=X, pady=(0, 5))

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, 
                              style="Progress.Horizontal.TProgressbar", length=100)
progress_bar.pack(fill=X)

converted_var = tk.StringVar(value=tr("converted_label").format(0, 0))
converted_label = ttk.Label(progress_status_frame, textvariable=converted_var, 
                           font=("Segoe UI", 10), anchor="e")
converted_label.pack(fill=X, pady=(0, 5))

# Status bar
status_frame = ttk.Frame(download_tab, padding=(0, 5))
status_frame.pack(fill=X, padx=15)

status_var = tk.StringVar(value=tr("status_waiting"))
status_label = ttk.Label(status_frame, textvariable=status_var, font=("Segoe UI", 12))
status_label.pack(fill=X)

# Download and Stop buttons
button_frame = ttk.Frame(download_tab, padding=(0, 15))
button_frame.pack(fill=X, padx=15)

button_container = ttk.Frame(button_frame)
button_container.pack(fill=X)

download_button = ttk.Button(button_container, text=tr("download"), 
                           style="Accent.TButton", width=15)
download_button.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))

stop_button = ttk.Button(button_container, text=tr("stop"), 
                       style="Stop.TButton", width=15, state="disabled")
stop_button.pack(side=LEFT, fill=X, expand=True)

# --- RANDOMIZING TAB ---
randomize_tab = ttk.Frame(tab_control)
tab_control.add(randomize_tab, text=tr("tab_randomize"))

# File operations section
random_frame = ttk.LabelFrame(randomize_tab, text=tr("randomize_section"), style="Card.TFrame", padding=15)
random_frame.pack(fill=BOTH, expand=True, padx=15, pady=10)

folder_ops_frame = ttk.Frame(random_frame)
folder_ops_frame.pack(fill=X, pady=(0, 15))

random_folder_var = tk.StringVar(value=tr("error_no_folder"))
random_folder_label = ttk.Label(folder_ops_frame, textvariable=random_folder_var)
random_folder_label.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))

random_folder_button = ttk.Button(folder_ops_frame, text=tr("choose_folder_random"), 
                                command=choose_random_folder, style="Accent.TButton")
random_folder_button.pack(side=RIGHT)

# File list display
file_list_frame = ttk.LabelFrame(random_frame, text=tr("file_list"), padding=10)
file_list_frame.pack(fill=BOTH, expand=True, pady=(10, 15))

# Create two listboxes with a scrollbar
columns_frame = ttk.Frame(file_list_frame)
columns_frame.pack(fill=BOTH, expand=True)

# Header labels
header_frame = ttk.Frame(columns_frame)
header_frame.pack(fill=X)

original_header = ttk.Label(header_frame, text=tr("original_name"), font=("Segoe UI", 10, "bold"))
original_header.pack(side=LEFT, padx=5, pady=5, fill=X, expand=True)

new_header = ttk.Label(header_frame, text=tr("new_name"), font=("Segoe UI", 10, "bold"))
new_header.pack(side=LEFT, padx=5, pady=5, fill=X, expand=True)

# Listboxes container
listboxes_frame = ttk.Frame(columns_frame)
listboxes_frame.pack(fill=BOTH, expand=True)

# Original filenames listbox (red text)
original_frame = tk.Frame(listboxes_frame, bg="white")
original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))

new_frame = tk.Frame(listboxes_frame, bg="white")
new_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0))

# Original filenames listbox (crveni tekst)
original_listbox = tk.Listbox(
    original_frame, 
    bg="white", 
    fg="red",
    font=("Segoe UI", 10),
    selectbackground="#ffe6e6",  # svetlija nijansa crvene za selekciju
    selectforeground="red",
    borderwidth=1,
    relief="solid",
    highlightthickness=0
)
original_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# New filenames listbox (zeleni tekst)
new_listbox = tk.Listbox(
    new_frame, 
    bg="white", 
    fg="green",
    font=("Segoe UI", 10),
    selectbackground="#e6ffe6",  # svetlija nijansa zelene za selekciju
    selectforeground="green",
    borderwidth=1,
    relief="solid",
    highlightthickness=0
)
new_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar
scrollbar = ttk.Scrollbar(listboxes_frame, orient="vertical")
scrollbar.pack(side=RIGHT, fill=Y)

# Link scrollbar to both listboxes
original_listbox.config(yscrollcommand=scrollbar.set)
new_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=lambda *args: multi_scroll(original_listbox, new_listbox, *args))

def multi_scroll(*listboxes):
    def _scroll(*args):
        for lb in listboxes:
            lb.yview(*args)
    return _scroll

# Status label for file operations
file_status_var = tk.StringVar()
file_status_label = ttk.Label(random_frame, textvariable=file_status_var)
file_status_label.pack(fill=X, pady=(5, 0))

sort_frame = ttk.Frame(random_frame)
sort_frame.pack(fill=X)

method_label = ttk.Label(sort_frame, text=tr("randomize_method"))
method_label.pack(side=LEFT, padx=(0, 10))

randomize_method = tk.StringVar(value="alphabetical")
alphabetical_radio = ttk.Radiobutton(sort_frame, text=tr("alphabetical"), variable=randomize_method, 
                   value="alphabetical")
alphabetical_radio.pack(side=LEFT, padx=5)

by_artist_radio = ttk.Radiobutton(sort_frame, text=tr("by_artist"), variable=randomize_method, 
                   value="by_artist")
by_artist_radio.pack(side=LEFT, padx=5)

random_radio = ttk.Radiobutton(sort_frame, text=tr("random"), variable=randomize_method, 
                   value="random")
random_radio.pack(side=LEFT, padx=5)

button_frame = ttk.Frame(random_frame)
button_frame.pack(fill=X, pady=(15, 5))

randomize_button = ttk.Button(button_frame, text=tr("randomize_button"), 
                            command=randomize_files, 
                            style="Accent.TButton", width=40)
randomize_button.pack(side=LEFT, padx=5)

remove_serial_button = ttk.Button(button_frame, text=tr("remove_serial_button"), 
                                command=remove_serial, 
                                width=40)
remove_serial_button.pack(side=LEFT, padx=5)

# --- BURNING TAB ---
burning_tab = ttk.Frame(tab_control)
tab_control.add(burning_tab, text=tr("tab_burning"))

# USB Burning Section
burn_frame = ttk.LabelFrame(burning_tab, text=tr("usb_burning"), style="Card.TFrame", padding=15)
burn_frame.pack(fill=BOTH, expand=True, padx=15, pady=10)

folder_burn_frame = ttk.Frame(burn_frame)
folder_burn_frame.pack(fill=X, pady=(0, 10))

burn_folder_label = ttk.Label(folder_burn_frame, text=tr("burn_folder"))
burn_folder_label.pack(side=LEFT, padx=(0, 10))

burn_folder_var = tk.StringVar(value=tr("select_folder"))
burn_folder_display = ttk.Label(folder_burn_frame, textvariable=burn_folder_var)
burn_folder_display.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))

def choose_burn_folder():
    folder = filedialog.askdirectory()
    if folder:
        burn_folder_var.set(folder)
burn_folder_button = ttk.Button(
    folder_burn_frame, 
    text=tr("choose_burn_folder"), 
    command=choose_burn_folder,
    style="Accent.TButton"
)
burn_folder_button.pack(side=RIGHT)

usb_frame = ttk.Frame(burn_frame)
usb_frame.pack(fill=X, pady=(0, 10))

usb_label = ttk.Label(usb_frame, text=tr("select_usb"))
usb_label.pack(side=LEFT, padx=(0, 10))

usb_var = tk.StringVar()
usb_combo = ttk.Combobox(usb_frame, textvariable=usb_var, state="readonly", width=30)
usb_combo.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))

refresh_button = ttk.Button(
    usb_frame, 
    text=tr("refresh"), 
    command=refresh_usb_drives,
    width=10
)
refresh_button.pack(side=RIGHT)

# New button container for 50/50 layout
button_container_frame = ttk.Frame(burn_frame)
button_container_frame.pack(fill=X, pady=(10, 5))

# Burn button - 50% width
burn_button = ttk.Button(
    button_container_frame, 
    text=tr("burn_usb"), 
    style="Accent.TButton",
    command=burn_to_usb
)
burn_button.pack(side=LEFT, expand=True, fill=X, padx=(0, 5))

# Stop burn button - 50% width
stop_burn_button = ttk.Button(
    button_container_frame, 
    text="✋ STOP BURN",
    style="Stop.TButton",
    state="disabled"
)
stop_burn_button.pack(side=LEFT, expand=True, fill=X, padx=(5, 0))

usb_status_var = tk.StringVar(value="")
usb_status_label = ttk.Label(burn_frame, textvariable=usb_status_var, wraplength=500)
usb_status_label.pack(fill=X, pady=(5, 0))

usb_progress_frame = ttk.Frame(burn_frame)
usb_progress_frame.pack(fill=X, pady=5)

usb_progress_var = tk.DoubleVar()
usb_progress_bar = ttk.Progressbar(
    usb_progress_frame, 
    variable=usb_progress_var, 
    maximum=100,
    style="Progress.Horizontal.TProgressbar"
)
usb_progress_bar.pack(fill=X)

# Initialize USB progress text
usb_progress_text = tk.StringVar()
update_usb_progress_display()  # Set initial value
usb_progress_label = ttk.Label(burn_frame, textvariable=usb_progress_text)
usb_progress_label.pack(fill=X)

# --- ABOUT TAB ---
about_tab = ttk.Frame(tab_control)
tab_control.add(about_tab, text="ℹ️ " + tr("tab_about"))

# Main container with padding
about_container = ttk.Frame(about_tab, padding=20)
about_container.pack(fill=BOTH, expand=True)

# Program description section - Two column layout
desc_frame = ttk.LabelFrame(about_container, text="📝 " + tr("program_description"), padding=15)
desc_frame.pack(fill=X, pady=(0, 15))

# Create a frame for the two columns
desc_columns = ttk.Frame(desc_frame)
desc_columns.pack(fill=BOTH, expand=True)

# Left column - Description
left_desc = ttk.Frame(desc_columns)
left_desc.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 15))

desc_label = ttk.Label(left_desc, text=tr("about_description_left"), justify=LEFT)
desc_label.pack(fill=X)

# Right column - Features
right_desc = ttk.Frame(desc_columns)
right_desc.pack(side=LEFT, fill=BOTH, expand=True)

features_label = ttk.Label(right_desc, text=tr("about_features_right"), justify=LEFT)
features_label.pack(fill=X)

# How to use section
usage_frame = ttk.LabelFrame(about_container, text="🛠️ " + tr("how_to_use"), padding=15)
usage_frame.pack(fill=X, pady=(0, 15))

usage_label = ttk.Label(usage_frame, text=tr("usage_instructions_text"), justify=LEFT)
usage_label.pack(fill=X)

# Developer info section
dev_frame = ttk.LabelFrame(about_container, text="👨‍💻 " + tr("developer_info"), padding=15)
dev_frame.pack(fill=X, pady=(0, 15))

# Create a frame for developer info with clickable links
dev_info_frame = ttk.Frame(dev_frame)
dev_info_frame.pack(fill=X)

# First part of the text (before links)
dev_text_part1 = ttk.Label(dev_info_frame, text=tr("developer_info_text").split("GitHub:")[0], justify=LEFT)
dev_text_part1.pack(anchor="w")

# GitHub link
github_frame = ttk.Frame(dev_info_frame)
github_frame.pack(anchor="w", fill=X)

github_bullet = ttk.Label(github_frame, text="• GitHub:", justify=LEFT)
github_bullet.pack(side=LEFT)

github_link = ttk.Label(github_frame, text="emrahponjevic", foreground="blue", cursor="hand2")
github_link.pack(side=LEFT)
github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/emrahponjevic"))

# LinkedIn link
linkedin_frame = ttk.Frame(dev_info_frame)
linkedin_frame.pack(anchor="w", fill=X)

linkedin_bullet = ttk.Label(linkedin_frame, text="• LinkedIn:", justify=LEFT)
linkedin_bullet.pack(side=LEFT)

linkedin_link = ttk.Label(linkedin_frame, text="Emrah Ponjevic", foreground="blue", cursor="hand2")
linkedin_link.pack(side=LEFT)
linkedin_link.bind("<Button-1>", lambda e: webbrowser.open("https://www.linkedin.com/in/emrah-ponjevic"))

# Donation section
donation_frame = ttk.LabelFrame(about_container, text="💖 " + tr("support_project"), padding=15)
donation_frame.pack(fill=X)

donation_label = ttk.Label(donation_frame, text=tr("donation_appeal_text"), justify=LEFT)
donation_label.pack(fill=X, pady=(0, 10))

# Donation button - now full width
donate_button = ttk.Button(
    donation_frame,
    text="💰 " + tr("donate_now"),
    command=show_donation_popup,
    style="Accent.TButton"
)
donate_button.pack(fill=X)  # Full width

# Version info at the bottom
version_frame = ttk.Frame(about_container)
version_frame.pack(fill=X, pady=(15, 0))

version_label = ttk.Label(
    version_frame, 
    text=tr("version_info"), 
    font=("Segoe UI", 9, "italic"),
    foreground="gray"
)
version_label.pack(side=RIGHT)

# --- Queue and threading ---
download_queue = queue.Queue()
status_queue = queue.Queue()
usb_queue = queue.Queue()

MAX_CONCURRENT_DOWNLOADS = 4
download_semaphore = threading.Semaphore(MAX_CONCURRENT_DOWNLOADS)

active_downloads = 0
download_progress = {}
folder_opened = False
item_counter = 1
download_active = False
total_items = 0
completed_items = 0

def ytdlp_download(url, path, media, file_format, bitrate, resolution, normalize, status_queue, item_id):
    global completed_items
    attempt = 1
    success = False
    item_completed = False
    
    while attempt <= MAX_DOWNLOAD_ATTEMPTS and not success:
        try:
            if attempt > 1:
                status_queue.put(("status", item_id, tr("status_retrying").format(attempt=attempt, max_attempts=MAX_DOWNLOAD_ATTEMPTS)))
            
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            
            ydl_opts = {
                "outtmpl": os.path.join(path, '%(title)s.%(ext)s'),
                "ffmpeg_args": ["-threads", "0"],
                "ca_certs": certifi.where(),
                "ffmpeg_location": resource_path("ffmpeg_binaries"),
            }
            
            if media == "audio":
                if bitrate:
                    bitrate_value = bitrate.split()[0]
                else:
                    bitrate_value = "256"
                    
                audio_args = []
                codec = file_format.strip('.')
                
                if codec == "mp3":
                    vbr_quality = {
                        "128": "5",
                        "192": "3",
                        "256": "2",
                        "320": "0"
                    }.get(bitrate_value, "2")
                    audio_args = ["-q:a", vbr_quality]
                else:
                    audio_args = ["-b:a", bitrate_value + "k"]
                
                if normalize:
                    audio_args.extend(["-af", "loudnorm"])
                    
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': codec,
                    }],
                    "postprocessor_args": audio_args,
                    "quiet": True,
                    "no_warnings": True,
                    "progress_hooks": [lambda d: progress_hook(d, status_queue, item_id)],
                })
            else:  # Video download
                codec = file_format.strip('.')  # Remove the dot from file_format (e.g., '.mp4' -> 'mp4')
                res_value = re.search(r'\d+', resolution)
                height = res_value.group() if res_value else "1080"
                format_selector = f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
                
                # Add postprocessor for video format conversion
                postprocessors = []
                if codec != "mp4":  # If the desired format is not mp4, add FFmpegVideoConvertor
                    postprocessors.append({
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': codec,  # Use the specified format (avi, mov, etc.)
                    })
                
                ydl_opts.update({
                    "format": format_selector,
                    "merge_output_format": codec,  # Set the final output format
                    "postprocessors": postprocessors,
                    "postprocessor_args": ["-movflags", "+faststart"] if codec == "mp4" else [],  # Only use faststart for mp4
                    "quiet": True,
                    "no_warnings": True,
                    "progress_hooks": [lambda d: progress_hook(d, status_queue, item_id)],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', tr("video"))
                
                temp_filename = ydl.prepare_filename(info)
                
                if media == "audio":
                    base, _ = os.path.splitext(temp_filename)
                    final_filename = base + file_format
                else:
                    base, _ = os.path.splitext(temp_filename)
                    final_filename = base + f".{codec}"  # Ensure the correct extension for video
                
                status_queue.put(("start", item_id, ""))
                ydl.download([url])
                
                if os.path.exists(final_filename) and os.path.getsize(final_filename) > 0:
                    status_queue.put(("success", item_id, tr("status_download_complete")))
                    success = True
                else:
                    error_msg = tr("error_file_empty")
                    if attempt == MAX_DOWNLOAD_ATTEMPTS:
                        status_queue.put(("error", item_id, error_msg))
                    else:
                        status_queue.put(("status", item_id, f"{error_msg} - {tr('status_retrying').format(attempt=attempt+1, max_attempts=MAX_DOWNLOAD_ATTEMPTS)}"))
                
        except Exception as e:
            error_msg = str(e)
            
            if "Private video" in error_msg:
                error_msg = tr("error_private_video")
            elif "blocked it" in error_msg or "not available" in error_msg:
                error_msg = tr("error_geo_restricted")
            elif "File is empty" in error_msg:
                error_msg = tr("error_file_empty")
            else:
                error_msg = tr("error_video_format").format(error=error_msg)
            
            if attempt == MAX_DOWNLOAD_ATTEMPTS:
                status_queue.put(("error", item_id, error_msg))
            else:
                status_queue.put(("status", item_id, f"{error_msg} - {tr('status_retrying').format(attempt=attempt+1, max_attempts=MAX_DOWNLOAD_ATTEMPTS)}"))
        
        if attempt == MAX_DOWNLOAD_ATTEMPTS and not success and not item_completed:
            status_queue.put(("completed", item_id, 100))
            completed_items += 1
            item_completed = True
        
        if success and not item_completed:
            status_queue.put(("completed", item_id, 100))
            completed_items += 1
            item_completed = True
        
        if not success and attempt < MAX_DOWNLOAD_ATTEMPTS:
            time.sleep(2)
        
        attempt += 1
    
    if not item_completed:
        status_queue.put(("error", item_id, tr("status_failed_after_retries").format(max_attempts=MAX_DOWNLOAD_ATTEMPTS)))
        status_queue.put(("completed", item_id, 100))
        completed_items += 1

def progress_hook(d, status_queue, item_id):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
        downloaded = d.get('downloaded_bytes', 0)
        percent = downloaded / total * 100 if total else 0
        status_queue.put(("downloading", item_id, percent))
    elif d['status'] == 'finished':
        status_queue.put(("converting", item_id, ""))

def download_worker():
    global active_downloads, download_active
    while download_active:
        try:
            item = download_queue.get(timeout=1)
            if item is None:
                break
        except queue.Empty:
            continue
            
        with download_semaphore:
            url, item_id = item
            active_downloads += 1
            try:
                resolution_value = resolution_combo.get() if media_type.get() == "video" else ""
                bitrate_value = bitrate_combo.get() if media_type.get() == "audio" else ""
                
                ytdlp_download(url, save_path_var.get(), media_type.get(), format_combo.get(), 
                              bitrate_value, resolution_value, normalize_var.get(), status_queue, item_id)
            except Exception as e:
                status_queue.put(("error", item_id, f"Unexpected error: {str(e)}"))
                status_queue.put(("completed", item_id, 100))
                completed_items += 1
            finally:
                active_downloads -= 1
                download_queue.task_done()

def start_download():
    global folder_opened, item_counter, download_active, total_items, completed_items
    links = link_entry.get().strip()
    if not links:
        messagebox.showerror(tr("error"), tr("error_no_link"))
        return
    if save_path_var.get() == tr("error_no_folder"):
        messagebox.showerror(tr("error"), tr("error_no_folder"))
        return

    status_var.set(tr("status_analyzing")) 
    root.update() 

    urls = [line.strip() for line in links.splitlines() if line.strip()]
    if not urls:
        messagebox.showerror(tr("error"), tr("error_no_link"))
        return

    folder_opened = False
    download_active = True
    total_items = 0
    completed_items = 0
    converted_var.set(tr("converted_label").format(0, 0))
    for item in tree.get_children():
        tree.delete(item)
    download_progress.clear()
    item_counter = 1

    download_button.config(state="disabled")
    stop_button.config(state="normal")

    for url in urls:
        try:
            with yt_dlp.YoutubeDL({
                'quiet': True, 
                'skip_download': True,
                'ignoreerrors': True,
                'extract_flat': 'in_playlist',
            }) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    entries = info['entries']
                    total_items += len(entries)
                    
                    update_interval = max(1, len(entries) // 10) if len(entries) > 10 else 1
                    
                    for idx, entry in enumerate(entries, 1):
                        if idx % update_interval == 0 or idx == len(entries):
                            status_var.set(tr("status_playlist_item").format(current=idx, total=len(entries)))
                            root.update_idletasks()
                        
                        if entry is None:
                            continue
                            
                        try:
                            entry_url = entry.get('url', url)
                            title = entry.get('title', f"{tr('video')} {idx}")
                            
                            item_id = tree.insert("", "end", values=(item_counter, title, tr("status_waiting_item")))
                            download_queue.put((entry_url, item_id))
                            download_progress[item_id] = 0
                            item_counter += 1
                            
                        except Exception as e:
                            continue
                else:
                    title = info.get('title', url)
                    item_id = tree.insert("", "end", values=(item_counter, title, tr("status_waiting_item")))
                    download_queue.put((url, item_id))
                    download_progress[item_id] = 0
                    item_counter += 1
                    total_items += 1
                    
        except Exception as e:
            item_id = tree.insert("", "end", values=(item_counter, url, tr("status_error_item")))
            download_progress[item_id] = 100
            item_counter += 1
            total_items += 1
            completed_items += 1

    converted_var.set(tr("converted_label").format(completed_items, total_items))
    status_var.set(tr("status_start"))
    
    for _ in range(MAX_CONCURRENT_DOWNLOADS):
        threading.Thread(target=download_worker, daemon=True).start()

def stop_download():
    global download_active
    download_active = False
    
    while not download_queue.empty():
        try:
            download_queue.get_nowait()
        except:
            break
    
    status_var.set(tr("status_stopped"))
    stop_button.config(state="disabled")
    download_button.config(state="normal")
    
    for item_id in tree.get_children():
        if tree.set(item_id, "status") == tr("status_waiting_item") or tr("status_downloading_item") in tree.set(item_id, "status"):
            tree.set(item_id, "status", tr("status_stopped_item"))

def show_success_popup():
    if messagebox.askyesno(tr("success_download"), tr("success_message")):
        try:
            os.startfile(save_path_var.get())
        except:
            pass

def check_status_queue():
    global folder_opened, download_active, completed_items
    try:
        while True:
            msg = status_queue.get_nowait()
            if msg[0] == "downloading":
                _, item_id, percent = msg
                tree.set(item_id, "status", f"{tr('status_downloading').format(percent=percent)}")
                download_progress[item_id] = percent
                
                if download_progress:
                    avg_progress = sum(download_progress.values()) / len(download_progress)
                    progress_var.set(avg_progress)
                    status_var.set(tr("status_downloading").format(percent=avg_progress))
            
            elif msg[0] == "converting":
                _, item_id, _ = msg
                tree.set(item_id, "status", tr("status_converting_item"))
                
            elif msg[0] == "file_check":
                _, item_id, filename = msg
                tree.set(item_id, "status", tr("status_file_check"))
                
            elif msg[0] == "success":
                _, item_id, status = msg
                tree.set(item_id, "status", status)
                
            elif msg[0] == "start":
                _, item_id, _ = msg
                tree.set(item_id, "status", tr("status_start"))
                download_progress[item_id] = 0
                
            elif msg[0] == "completed":
                _, item_id, percent = msg
                download_progress[item_id] = percent
                
            elif msg[0] == "error":
                _, item_id, error = msg
                if item_id:
                    tree.set(item_id, "status", tr("status_error_item"))
                status_var.set(f"{tr('status_error')}: {error}")
                
            converted_var.set(tr("converted_label").format(completed_items, total_items))
            root.update_idletasks()
    except queue.Empty:
        pass
    
    if download_progress:
        total_progress = sum(download_progress.values())
        avg_progress = total_progress / len(download_progress)
        progress_var.set(avg_progress)
        status_var.set(tr("status_downloading").format(percent=avg_progress))
    
    converted_var.set(tr("converted_label").format(completed_items, total_items))
    
    if (download_active and total_items > 0 and 
        completed_items >= total_items and 
        active_downloads == 0 and 
        not folder_opened):
        folder_opened = True
        download_active = False
        stop_button.config(state="disabled")
        download_button.config(state="normal")
        status_var.set(tr("status_finished"))
        progress_var.set(100)
        show_success_popup()
    
    root.after(200, check_status_queue)

# --- USB Queue Handler ---
def check_usb_queue():
    global current_usb_copied, current_usb_total, last_usb_status_key, last_usb_status_args
    
    try:
        while True:
            msg = usb_queue.get_nowait()
            if msg[0] == "status":
                last_usb_status_key = msg[1]
                last_usb_status_args = msg[2:] if len(msg) > 2 else None
                translated = tr(msg[1])
                if last_usb_status_args:
                    translated = translated.format(*last_usb_status_args)
                usb_status_var.set(translated)
                
            elif msg[0] == "progress":
                current_usb_copied = msg[1]
                current_usb_total = msg[2]
                update_usb_progress_display()
                usb_progress_var.set(msg[3])
                
               # --- DODAJTE OVAJ BLOK ---
            elif msg[0] == "progress_bar":
                # msg[1] će biti vrijednost od 0 do 100
                usb_progress_var.set(msg[1])
                # Resetujemo text label jer progress bar sada pokazuje status
                usb_progress_text.set("")     
                
            elif msg[0] == "error":
                messagebox.showerror(tr("error"), tr(msg[1]))
                
            elif msg[0] == "success":
                messagebox.showinfo(tr("success"), tr(msg[1]))
                
            elif msg[0] == "enable_buttons":
                burn_button.config(state="normal")
                refresh_button.config(state="normal")
                usb_progress_var.set(0)
                
    except queue.Empty:
        pass
    root.after(200, check_usb_queue)

# --- Update UI texts on language change ---
def update_ui_texts():
    root.title(tr("app_title"))
    title_label.config(text=tr("app_title"))
    link_label.config(text=tr("youtube_link"))
    language_label.config(text=tr("language"))
    options_frame.config(text=tr("options"))
    audio_radio.config(text=tr("media_audio"))
    video_radio.config(text=tr("media_video"))
    format_label.config(text=tr("format"))
    bitrate_label.config(text=tr("bitrate"))
    resolution_label.config(text=tr("resolution"))
    normalize_check.config(text=tr("normalize_audio"))
    folder_button.config(text=tr("choose_folder"))
    list_frame.config(text=tr("list_for_download"))
    random_frame.config(text=tr("randomize_section"))
    random_folder_button.config(text=tr("choose_folder_random"))
    randomize_button.config(text=tr("randomize_button"))
    remove_serial_button.config(text=tr("remove_serial_button"))
    download_button.config(text=tr("download"))
    stop_button.config(text=tr("stop"))
    save_path_var.set(tr("error_no_folder"))
    random_folder_var.set(tr("error_no_folder"))
    status_var.set(tr("status_waiting"))
    method_label.config(text=tr("randomize_method"))
    import_label.config(text=tr("import_label"))
    import_button.config(text=tr("import_button"))
    burn_frame.config(text=tr("usb_burning"))
    burn_folder_label.config(text=tr("burn_folder"))
    burn_folder_var.set(tr("select_folder"))
    burn_folder_button.config(text=tr("choose_burn_folder"))
    usb_label.config(text=tr("select_usb"))
    refresh_button.config(text=tr("refresh"))
    burn_button.config(text=tr("burn_usb"))
    tree.heading("no", text=tr("column_no"))
    tree.heading("file", text=tr("column_file"))
    tree.heading("status", text=tr("column_status"))
    usb_status_var.set("")
    converted_var.set(tr("converted_label").format(completed_items, total_items))
    
    alphabetical_radio.config(text=tr("alphabetical"))
    by_artist_radio.config(text=tr("by_artist"))
    random_radio.config(text=tr("random"))
    
    tab_control.tab(0, text=tr("tab_download"))
    tab_control.tab(1, text=tr("tab_randomize"))
    tab_control.tab(2, text=tr("tab_burning"))
    tab_control.tab(3, text=tr("tab_about"))
    
    original_header.config(text=tr("original_name"))
    new_header.config(text=tr("new_name"))
    file_list_frame.config(text=tr("file_list"))
    
# Update About tab texts
    desc_frame.config(text="📝 " + tr("program_description"))
    usage_frame.config(text="🛠️ " + tr("how_to_use"))
    dev_frame.config(text="👨‍💻 " + tr("developer_info"))
    donation_frame.config(text="💖 " + tr("support_project"))
    donate_button.config(text="💰 " + tr("donate_now"))
    
    desc_label.config(text=tr("about_description_left"))
    features_label.config(text=tr("about_features_right"))
    usage_label.config(text=tr("usage_instructions_text"))
    
    # Update the first part of developer info text
    dev_text_part1.config(text=tr("developer_info_text").split("GitHub:")[0])
    
    # The links themselves don't need updating as they're fixed URLs
    # But we might want to update the bullet points if they're translated
    github_bullet.config(text="• " + tr("GitHub") + ":")
    linkedin_bullet.config(text="• " + tr("LinkedIn") + ":")
    
    donation_label.config(text=tr("donation_appeal_text"))
    version_label.config(text=tr("version_info"))
    
    if last_usb_status_key:
        translated = tr(last_usb_status_key)
        if last_usb_status_args:
            translated = translated.format(*last_usb_status_args)
        usb_status_var.set(translated)
    
    update_usb_progress_display()
    refresh_usb_drives()


def language_changed(event=None):
    update_ui_texts()
language_combo.bind("<<ComboboxSelected>>", language_changed)

# Set button commands
download_button.config(command=start_download)
stop_button.config(command=stop_download)

# Start status check
check_status_queue()
check_usb_queue()

if usb_dependencies_available:
    refresh_usb_drives()
else:
    usb_combo['values'] = [tr("no_usb")]
    usb_combo.current(0)

# Initialize UI
update_ui_texts()

# Apply theme for the first time
update_theme()

root.mainloop()