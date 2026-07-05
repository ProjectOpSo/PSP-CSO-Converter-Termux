#!/usr/bin/env python3

import shutil
import subprocess
import sys
import os
from pathlib import Path
from time import sleep
import threading

def detect_storage():
    candidates = [
        Path("/sdcard"),
        Path("/storage/emulated/0"),
        Path(os.getenv("EXTERNAL_STORAGE", "")),
        Path.home() / "storage/shared"
    ]
    for c in candidates:
        if c and c.exists():
            return c
    return Path("/sdcard")

BASE_STORAGE = detect_storage()

ISO_DIR = BASE_STORAGE / "Download" / "Iso"
ZSO_DIR = BASE_STORAGE / "Download" / "Zso"

ZISO = "/data/data/com.termux/files/home/Open-PS2-Loader/pc/ziso.py"
COMP_LEVEL = "2"
LANGUAGE = None

class Colors:
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

conversion_results = []

def clear_screen():
    subprocess.run(['clear'], check=False)

def print_separator(length=50):
    print(f"{Colors.WHITE}{'=' * length}{Colors.END}")

def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

TRANSLATIONS = {
    "pt_BR": {
        "language_menu_title": "SELECAO DE IDIOMA",
        "language_separator": "==================================================",
        "language_select": "Escolha: ",
        "language_invalid": "[ERRO] Opcao invalida. Digite 1 ou 2.",
        "iso_handling_title": "PREFERENCIA DE TRATAMENTO ISO",
        "iso_option_1": "  [1] Manter arquivos ISO apos compressao",
        "iso_option_2": "  [2] Remover arquivos ISO apos compressao",
        "iso_separator": "==================================================",
        "iso_select": "Escolha: ",
        "iso_invalid": "[ERRO] Opcao invalida. Digite 1 ou 2.",
        "dir_not_found": "[ERRO] Diretorio nao encontrado: {path}",
        "no_iso_files": "[INFO] Nenhum arquivo ISO encontrado em {path}",
        "processing": "[{index}/{total}] Processando: {filename}",
        "skip_exists": "[PULAR] Arquivo ZSO ja existe no destino.",
        "error_compression": "[ERRO] Falha na compressao.",
        "error_invalid_zso": "[ERRO] Arquivo ZSO invalido gerado.",
        "error_move": "[ERRO] Falha ao mover arquivo para pasta Zso.",
        "ok_moved": "[OK] Arquivo movido com sucesso.",
        "ok_kept": "[OK] ISO mantida",
        "ok_deleted": "[OK] ISO deletada",
        "error_exception": "[ERRO] {error}",
        "compression_progress": "[COMPRIMINDO...]",
        "summary_title": "RESUMO FINAL",
        "summary_separator": "==================================================",
        "summary_found": "Arquivos ISO encontrados",
        "summary_converted": "Convertidos com sucesso",
        "summary_failed": "Falhados/Pulados",
        "summary_iso_status": "Arquivos ISO",
        "iso_kept": "Mantidos",
        "iso_removed": "Removidos",
        "starting": "INICIANDO COMPRESSAO",
        "detailed_results": "RESULTADOS DETALHADOS",
        "rom_name": "ROM",
        "iso_size_header": "Tamanho ISO",
        "zso_size_header": "Tamanho ZSO",
        "reduction_header": "Reducao",
    },
    "en_US": {
        "language_menu_title": "LANGUAGE SELECTION",
        "language_separator": "==================================================",
        "language_select": "Choose: ",
        "language_invalid": "[ERROR] Invalid choice. Please enter 1 or 2.",
        "iso_handling_title": "ISO HANDLING PREFERENCE",
        "iso_option_1": "  [1] Keep ISO files after compression",
        "iso_option_2": "  [2] Remove ISO files after compression",
        "iso_separator": "==================================================",
        "iso_select": "Choose: ",
        "iso_invalid": "[ERROR] Invalid choice. Please enter 1 or 2.",
        "dir_not_found": "[ERROR] Directory not found: {path}",
        "no_iso_files": "[INFO] No ISO files found in {path}",
        "processing": "[{index}/{total}] Processing: {filename}",
        "skip_exists": "[SKIP] ZSO file already exists in destination.",
        "error_compression": "[ERROR] Compression failed.",
        "error_invalid_zso": "[ERROR] Invalid ZSO file generated.",
        "error_move": "[ERROR] Failed to move file to Zso folder.",
        "ok_moved": "[OK] File moved successfully.",
        "ok_kept": "[OK] ISO kept",
        "ok_deleted": "[OK] ISO deleted",
        "error_exception": "[ERROR] {error}",
        "compression_progress": "[COMPRESSING...]",
        "summary_title": "SUMMARY",
        "summary_separator": "==================================================",
        "summary_found": "ISO files found",
        "summary_converted": "Successfully converted",
        "summary_failed": "Failed/Skipped",
        "summary_iso_status": "ISO files",
        "iso_kept": "Kept",
        "iso_removed": "Removed",
        "starting": "STARTING COMPRESSION",
        "detailed_results": "DETAILED RESULTS",
        "rom_name": "ROM",
        "iso_size_header": "ISO Size",
        "zso_size_header": "ZSO Size",
        "reduction_header": "Reduction",
    }
}

progress_percentage = 0
compression_active = False

def t(key, lang="pt_BR", **kwargs):
    text = TRANSLATIONS[lang][key]
    return text.format(**kwargs) if kwargs else text

def get_language():
    clear_screen()
    while True:
        print_separator()
        print("SELECAO DE IDIOMA")
        print_separator()
        print()
        print("  [1] Portugues Brasileiro")
        print("  [2] English (American)")
        print()
        choice = input("> ").strip()
        if choice == "1":
            return "pt_BR"
        if choice == "2":
            return "en_US"
        print("\n[ERRO] Opcao invalida\n")
        sleep(1)

def get_user_preference(language):
    while True:
        print_separator()
        print(t("iso_handling_title", lang=language))
        print_separator()
        print()
        print(t("iso_option_1", lang=language))
        print(t("iso_option_2", lang=language))
        print()
        choice = input("> ").strip()
        if choice == "1":
            return True
        if choice == "2":
            return False
        print(t("iso_invalid", lang=language))

def simulate_progress(process, total_time=100):
    global progress_percentage, compression_active
    start_time = __import__('time').time()
    while process.poll() is None and compression_active:
        elapsed = __import__('time').time() - start_time
        progress_percentage = min(int((elapsed / total_time) * 100), 99)
        sleep(0.1)
    if compression_active:
        progress_percentage = 100

def show_progress_screen(filename, language):
    global progress_percentage, compression_active
    bar_width = 40
    while compression_active and progress_percentage < 100:
        clear_screen()
        print_separator()
        print(t("processing", lang=language, index="", total="", filename=filename))
        print_separator()
        print()
        filled = int(bar_width * progress_percentage / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        print(f"[{bar}] {progress_percentage}%")
        sleep(0.2)
    clear_screen()
    print_separator()
    print(t("processing", lang=language, index="", total="", filename=filename))
    print_separator()
    print()
    print("█" * bar_width + " 100%")
    sleep(0.5)

def move_file_safely(src, dst):
    try:
        shutil.move(str(src), str(dst))
        return True
    except:
        try:
            subprocess.run(['cp', str(src), str(dst)], check=True, capture_output=True)
            os.remove(str(src))
            return True
        except:
            return False

def main():
    global LANGUAGE, progress_percentage, compression_active, conversion_results
    LANGUAGE = get_language()
    clear_screen()

    ZSO_DIR.mkdir(parents=True, exist_ok=True)

    if not ISO_DIR.exists():
        print(t("dir_not_found", lang=LANGUAGE, path=ISO_DIR))
        return

    iso_files = sorted(ISO_DIR.glob("*.iso"))
    if not iso_files:
        print(t("no_iso_files", lang=LANGUAGE, path=ISO_DIR))
        return

    keep_isos = get_user_preference(LANGUAGE)

    total_files = len(iso_files)
    converted_files = 0

    for index, iso_file in enumerate(iso_files, start=1):
        game_name = iso_file.stem
        temp_zso = ISO_DIR / f"{game_name}.zso"
        final_zso = ZSO_DIR / f"{game_name}.zso"

        if final_zso.exists():
            continue

        iso_size = iso_file.stat().st_size

        command = ["python", ZISO, "-c", COMP_LEVEL, str(iso_file), str(temp_zso)]

        try:
            progress_percentage = 0
            compression_active = True

            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            thread = threading.Thread(target=simulate_progress, args=(process, 100))
            thread.daemon = True
            thread.start()

            show_progress_screen(iso_file.name, LANGUAGE)
            process.wait()
            compression_active = False

            if process.returncode != 0:
                continue

            if not temp_zso.exists():
                continue

            zso_size = temp_zso.stat().st_size
            move_file_safely(temp_zso, final_zso)

            if not keep_isos:
                iso_file.unlink()

            conversion_results.append({
                "name": game_name,
                "iso_size": iso_size,
                "zso_size": zso_size,
                "reduction": ((iso_size - zso_size) / iso_size) * 100
            })

            converted_files += 1

        except:
            continue

    print("DONE")

if __name__ == "__main__":
    main()
