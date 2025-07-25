import os
import sys
import argparse
import subprocess

try:
    import magic
except ImportError:
    magic = None

class color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

SUSPICIOUS_FOR_TEXT = {
    "mp3", "mp4", "avi", "jpg", "png", "gif", "pdf", "zip", "rar", "7z",
    "exe", "apk", "so", "dll", "iso", "docx", "xlsx", "pptx", "tar", "gz",
    "mov", "mkv", "flac", "wav", "webm", "rm", "ts", "wmv", "m4v", "3gp"
}

# Added script extensions here:
SCRIPT_EXTENSIONS = {"bat", "sh", "exe", "gradle", "ps1", "cmd"}

delete_text_disguises = False

VIDEO_SIGNATURES = {
    b'\x1A\x45\xDF\xA3': 'mkv/webm',
    b'\x46\x4C\x56': 'flv',
    b'\x30\x26\xB2\x75\x8E\x66': 'wmv',
    b'\x2E\x52\x4D\x46': 'rm',
}

mp4_brands = [b'isom', b'iso2', b'avc1', b'mp41', b'mp42', b'3gp4', b'M4V ', b'M4A ', b'qt  ']

magic_signatures = {
    b"\xFF\xD8\xFF": "jpg",
    b"\x89\x50\x4E\x47": "png",
    b"\x47\x49\x46\x38": "gif",
    b"\x25\x50\x44\x46": "pdf",
    b"\x50\x4B\x03\x04": "zip",
    b"\x52\x61\x72\x21": "rar",
    b"\x49\x44\x33": "mp3",
    b"\x4D\x5A": "exe",
    b"\x7F\x45\x4C\x46": "elf",
    b"\x1F\x8B": "gz",
    b"\x37\x7A\xBC\xAF\x27\x1C": "7z"
}

EXT_LANG_MAP = {
    "py": "python", "js": "javascript", "html": "html", "htm": "html",
    "css": "css", "txt": "plain text", "java": "java", "c": "c/c++", "cpp": "c/c++",
    "cs": "c#", "php": "php", "rb": "ruby", "go": "go", "rs": "rust", "swift": "swift",
    "kt": "kotlin", "m": "objective-c", "xml": "xml",
    # Script extensions mapping
    "bat": "batch script",
    "sh": "shell script",
    "ps1": "powershell",
    "cmd": "batch script",
    "gradle": "gradle script",
    "exe": "executable binary"
}

UNIQUE_TAGS = {
    "php": ["<?php"],
    "ruby": ["end\n", "puts "],
    "python": ["def ", "import ", "print(", "self"],
    "java": ["public class", "static void main", "System.out.println"],
    "c/c++": ["#include", "int main", "printf"],
    "c#": ["using System", "namespace", "Console.WriteLine"],
    "go": ["package main", "func main()", "import ", "fmt."],
    "rust": ["fn main()", "let mut", "use std::"],
    "swift": ["import UIKit", "let ", "func ", "var "],
    "kotlin": ["fun main", "val ", "var ", "println"],
    "objective-c": ["#import", "@interface", "@implementation"],
    "html": ["<!doctype html", "<html", "<head", "<body", "<script"],
    "css": ["color:", "font-", "margin:", "padding:", "background:"],
    "javascript": ["function ", "console.log", "var ", "let ", "const ", "=>", "document."],
    # Scripts unique tags
    "batch script": ["@echo off", "echo ", "rem "],
    "shell script": ["#!/bin/bash", "#!/bin/sh", "echo ", "fi", "then"],
    "powershell": ["param(", "Write-Host", "Get-"],
    "gradle script": ["plugins {", "dependencies {", "task "],
}

LANG_SIGNATURES = {
    "html": ["<!doctype html", "<html", "<head", "<body", "<script"],
    "css": ["color:", "font-", "margin:", "padding:", "background:", "{", "}"],
    "javascript": ["function ", "console.log", "var ", "let ", "const ", "=>", "document."],
    "python": ["def ", "import ", "print(", "self", "class ", "__name__"],
    "php": ["<?php", "$", "echo ", "->"],
    "ruby": ["def ", "end", "puts ", ":", "class "],
    "java": ["public class", "static void main", "System.out.println"],
    "c/c++": ["#include", "int main", "printf", "scanf"],
    "c#": ["using System", "namespace", "class ", "Console.WriteLine"],
    "go": ["package main", "func main()", "import ", "fmt."],
    "rust": ["fn main()", "let mut", "use std::"],
    "swift": ["import UIKit", "let ", "func ", "var "],
    "kotlin": ["fun main", "val ", "var ", "println"],
    "objective-c": ["#import", "@interface", "@implementation"],
    "xml": ["<?xml", "<note>", "<data>"],
    # Scripts normal tags
    "batch script": ["@echo off", "echo ", "rem "],
    "shell script": ["#!/bin/bash", "#!/bin/sh", "echo ", "fi", "then"],
    "powershell": ["param(", "Write-Host", "Get-"],
    "gradle script": ["plugins {", "dependencies {", "task "],
}

def detect_video_type(filepath):
    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)
            if len(header) > 12 and header[4:8] == b'ftyp':
                brand = header[8:12]
                if brand in mp4_brands:
                    return 'mp4/3gp/m4v/mov'
            if header.startswith(b'\x1A\x45\xDF\xA3'):
                return 'mkv/webm'
            if header.startswith(b'RIFF') and b'AVI ' in header[8:16]:
                return 'avi'
            for sig, name in VIDEO_SIGNATURES.items():
                if header.startswith(sig):
                    return name
            if header[0] == 0x47 and header[188] == 0x47:
                return 'ts'
    except:
        pass
    return None

def detect_magic_type(filepath):
    header_type = detect_video_type(filepath)
    if header_type:
        return header_type
    try:
        with open(filepath, 'rb') as f:
            file_start = f.read(64)
            if len(file_start) >= 12 and file_start[4:8] == b'ftyp':
                brand = file_start[8:12]
                if brand in mp4_brands:
                    return "mp4"
            for sig, ext in magic_signatures.items():
                if file_start.startswith(sig):
                    return ext
    except:
        return None
    return None

def is_probably_text(filepath):
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(2048)
            if not chunk:
                return True
            text_chars = bytearray(range(32, 127)) + b"\n\r\t\b"
            nontext = [b for b in chunk if b not in text_chars]
            return len(nontext) / len(chunk) < 0.05
    except:
        return False

def get_real_type(filepath):
    if magic:
        try:
            mime = magic.from_file(filepath, mime=True)
            if "text" in mime:
                return "txt"
            return mime.split("/")[-1]
        except:
            pass
    try:
        result = subprocess.run(['file', '--mime-type', filepath], capture_output=True, text=True)
        if result.returncode == 0:
            mime = result.stdout.strip().split(": ")[-1]
            if "text" in mime:
                return "txt"
            return mime.split("/")[-1]
    except:
        pass
    magic_ext = detect_magic_type(filepath)
    if magic_ext:
        return magic_ext
    if is_probably_text(filepath):
        return "txt"
    return "unknown"

def detect_text_language(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [f.readline().lower() for _ in range(30)]
            content = "".join(lines)

            scores = {}
            for lang in LANG_SIGNATURES.keys():
                score = 0
                unique_tags = UNIQUE_TAGS.get(lang, [])
                for tag in unique_tags:
                    if tag in content:
                        score += 3  # higher weight
                for tag in LANG_SIGNATURES[lang]:
                    if tag in content:
                        score += 1
                scores[lang] = score

            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

            if not sorted_scores:
                return ["plain text"]

            top_score = sorted_scores[0][1]
            if top_score == 0:
                return ["plain text"]

            suggestions = [sorted_scores[0][0]]
            for lang, score in sorted_scores[1:]:
                if top_score - score <= 1:
                    suggestions.append(lang)
                else:
                    break

            return suggestions

    except Exception:
        return ["plain text"]

def scan_folder_for_fake_extensions(folder_path, output_file="mismatched_files.txt"):
    mismatches, disguised_text_files, deleted_files = [], [], []

    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            current_ext = os.path.splitext(file)[-1].lower().replace(".", "")
            real_type = get_real_type(full_path)
            text_langs = None

            if not real_type:
                continue

            # Handle script extensions specially
            if current_ext in SCRIPT_EXTENSIONS:
                if real_type in ("txt", "unknown"):
                    text_langs = detect_text_language(full_path)
                else:
                    text_langs = [real_type]

                expected_lang = EXT_LANG_MAP.get(current_ext)
                if expected_lang and expected_lang not in text_langs:
                    mismatch_reason = f"Extension-language mismatch (Detected: {', '.join(text_langs)})"
                    mismatches.append((full_path, current_ext, ", ".join(text_langs), mismatch_reason))
                    print(f"{color.YELLOW}[LANGUAGE MISMATCH]{color.END} {file} (.{current_ext}) → Detected as {', '.join(text_langs)}")

                if real_type == "txt" and current_ext in SUSPICIOUS_FOR_TEXT.union(SCRIPT_EXTENSIONS):
                    disguised_text_files.append((full_path, current_ext, ", ".join(text_langs) if text_langs else "unknown"))
                    print(f"{color.RED}[DISGUISED SCRIPT TEXT]{color.END} {file} (.{current_ext}) → Detected as {', '.join(text_langs) if text_langs else 'unknown'}")
                    if delete_text_disguises:
                        try:
                            os.remove(full_path)
                            deleted_files.append(full_path)
                        except Exception as e:
                            disguised_text_files.append((full_path, current_ext, f"Deletion failed: {e}"))
                continue  # skip further processing for scripts

            # Normal processing for other files
            if real_type == "txt":
                text_langs = detect_text_language(full_path)
                expected_lang = EXT_LANG_MAP.get(current_ext)
                if expected_lang and expected_lang not in text_langs:
                    mismatch_reason = f"Extension-language mismatch (Detected: {', '.join(text_langs)})"
                    mismatches.append((full_path, current_ext, ", ".join(text_langs), mismatch_reason))
                    print(f"{color.YELLOW}[LANGUAGE MISMATCH]{color.END} {file} (.{current_ext}) → Detected as {', '.join(text_langs)}")

            if real_type == "txt" and current_ext in SUSPICIOUS_FOR_TEXT:
                disguised_text_files.append((full_path, current_ext, ", ".join(text_langs) if text_langs else "unknown"))
                print(f"{color.RED}[DISGUISED TEXT]{color.END} {file} (.{current_ext}) → Detected as {', '.join(text_langs) if text_langs else 'unknown'}")
                if delete_text_disguises:
                    try:
                        os.remove(full_path)
                        deleted_files.append(full_path)
                    except Exception as e:
                        disguised_text_files.append((full_path, current_ext, f"Deletion failed: {e}"))

            elif current_ext and current_ext != real_type and real_type != "txt":
                mismatches.append((full_path, current_ext, real_type, "Extension-content mismatch"))
                print(f"{color.CYAN}[CONTENT MISMATCH]{color.END} {file} (.{current_ext}) ≠ {real_type}")

    with open(output_file, "w", encoding='utf-8') as f:
        f.write("=== Extension Mismatches ===\n\n")
        for item in mismatches:
            f.write(f"File: {item[0]}\n  Extension: .{item[1]}\n  Detected: {item[2]}\n  Issue: {item[3]}\n\n")

        f.write("=== Text Disguised as Media/Binary ===\n\n")
        for item in disguised_text_files:
            f.write(f"File: {item[0]}\n  Extension: .{item[1]}\n  Detected language: {item[2]}\n\n")

        if delete_text_disguises:
            f.write("=== Deleted Files ===\n\n")
            for df in deleted_files:
                f.write(df + "\n")

    print(f"\n{color.BOLD}✅ Scan Complete{color.END}")
    print(f"{color.YELLOW}Extension mismatches: {len(mismatches)}{color.END}")
    print(f"{color.RED}Disguised text files: {len(disguised_text_files)}{color.END}")
    if delete_text_disguises:
        print(f"{color.GREEN}Deleted files: {len(deleted_files)}{color.END}")
    else:
        print(f"{color.CYAN}To enable deletion, set delete_text_disguises = True in script.{color.END}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect fake/mismatched file extensions with content language detection")
    parser.add_argument("path", help="Folder path to scan")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"{color.RED}❌ Error: '{args.path}' is not a valid folder.{color.END}")
        sys.exit(1)

    scan_folder_for_fake_extensions(args.path)
