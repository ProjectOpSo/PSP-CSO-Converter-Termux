# PSP-CSO-Converter-Termux

Convert PSP ISO games to CSO directly on Android using Termux.

## Features

- Batch ISO → CSO conversion
- Compression level fixed at 9 (maximum compression)
- Portuguese and English language support
- Detailed compression report
- Option to keep or remove original ISO files
- Automatic PSP-Iso and PSP-Cso folder creation
- Direct output to destination folder
- Clean terminal interface

## Requirements

- Android device
- Termux
- Storage permission granted
- ciso package installed
- git package installed

## Installation

**Update Termux packages:**

```bash
pkg update -y
pkg upgrade -y
```

**Install required packages:**

```bash
pkg install python -y
pkg install ciso -y
pkg install git -y
```

**Grant storage access:**

```bash
termux-setup-storage
```

**Clone this repository:**

```bash
git clone https://github.com/ProjectOpSo/PSP-CSO-Converter-Termux.git
```

**Enter the project directory:**

```bash
cd PSP-CSO-Converter-Termux
```

**Run the script:**

```bash
python compress_psp_isos.py
```

## Folder Structure

The script automatically creates:

- `/sdcard/Download/PSP-Iso`
- `/sdcard/Download/PSP-Cso`

Place your PSP ISO files inside:

```
/sdcard/Download/PSP-Iso
```

**Example:**

```
PSP-Iso
├── God of War - Chains of Olympus.iso
├── Tekken 6.iso
├── GTA Vice City Stories.iso
```

Compressed games will be saved to:

```
/sdcard/Download/PSP-Cso
```

**Example:**

```
PSP-Cso
├── God of War - Chains of Olympus.cso
├── Tekken 6.cso
├── GTA Vice City Stories.cso
```

## Usage

1. Start the script
2. Select your language
3. Choose whether to keep or remove ISO files after compression
4. Wait for conversion to finish
5. Review the final compression report

**Example Output:**

```
==================================================
STARTING COMPRESSION
==================================================

==================================================
[1/3] Processing: Tekken 6.iso
==================================================

Conversion completed

==================================================
[2/3] Processing: God of War - Chains of Olympus.iso
==================================================

Conversion completed
```

## Compression Information

This project uses:

```bash
ciso 9 input.iso output.cso
```

**Compression level:**

- `9` = Maximum Compression

## Notes

- Existing CSO files are skipped automatically
- ISO files can be kept or removed after conversion
- The script generates CSO files directly in the output directory
- Supports all PSP games stored as ISO images


