from pathlib import Path
from typing import Union
import docx2txt
import fitz
import pypandoc
import tempfile
import os
import subprocess

# Chỉ định đường dẫn thủ công đến pandoc.exe và soffice.exe
PANDOC_PATH = r"C:\Program Files\Pandoc\pandoc.exe"  # Đảm bảo đúng đường dẫn
LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"  # Đường dẫn đến soffice.exe

def parse_file_content(file_path: Union[str, Path]) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".docx":
        return parse_docx(path)
    elif suffix == ".pdf":
        return parse_pdf(path)
    elif suffix == ".doc":
        converted = convert_doc_to_docx(path)
        return parse_docx(converted) if converted else "[ERROR] Could not convert .doc to .docx"
    else:
        return ""

def parse_docx(path: Path) -> str:
    try:
        text = docx2txt.process(str(path))
        return text.strip()
    except Exception as e:
        return f"[DOCX ERROR] {str(e)}"

def parse_pdf(path: Path) -> str:
    try:
        doc = fitz.open(str(path))
        text = ""
        for page in doc:
            text += page.get_text("text")
        return text.strip()
    except Exception as e:
        return f"[PDF ERROR] {str(e)}"

def convert_doc_to_docx_with_libreoffice(doc_path: Path) -> Union[Path, None]:
    try:
        output_path = Path(tempfile.gettempdir()) / (doc_path.stem + ".docx")
        result = subprocess.run([
            LIBREOFFICE_PATH,
            "--headless",
            "--convert-to", "docx",
            "--outdir", str(tempfile.gettempdir()),
            str(doc_path)
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Đảm bảo file được flush
        if output_path.exists():
            return output_path
        else:
            raise Exception("LibreOffice failed to create .docx")
    except subprocess.CalledProcessError as e:
        print(f"[LIBREOFFICE ERROR] {str(e.stderr)}")
        return None
    except Exception as e:
        print(f"[CONVERT ERROR] {str(e)}")
        return None

def convert_doc_to_pdf(doc_path: Path) -> Union[Path, None]:
    try:
        # Ưu tiên dùng libreoffice để chuyển .doc sang .pdf trực tiếp
        if doc_path.suffix.lower() == ".doc":
            output_path = Path(tempfile.gettempdir()) / (doc_path.stem + ".pdf")
            result = subprocess.run([
                LIBREOFFICE_PATH,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(tempfile.gettempdir()),
                str(doc_path)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Đợi và kiểm tra file tồn tại
            import time
            time.sleep(2)  # Tăng thời gian chờ lên 2 giây
            print(f"LibreOffice conversion to {output_path}, checking existence: {output_path.exists()}")  # Debug log
            if output_path.exists():
                return output_path
            else:
                raise Exception("LibreOffice failed to convert .doc to .pdf")

        # Nếu là .docx, dùng pandoc
        elif doc_path.suffix.lower() == ".docx":
            if not pypandoc.get_pandoc_path():
                pypandoc.ensure_pandoc_installed()
                pypandoc.set_pandoc_path(PANDOC_PATH)
            pandoc_path = pypandoc.get_pandoc_path()
            if not pandoc_path or pandoc_path == "pandoc":
                raise Exception(f"Failed to set pandoc path to {PANDOC_PATH}")
            print(f"Using pandoc at: {pandoc_path}")  # Debug log
            output_path = Path(tempfile.gettempdir()) / (doc_path.stem + ".pdf")
            print(f"Converting {doc_path} to {output_path}")  # Debug log
            pypandoc.convert_file(str(doc_path), 'pdf', outputfile=str(output_path))
            print(f"Conversion completed, checking existence: {output_path.exists()}")  # Debug log
            return output_path if output_path.exists() else None
        else:
            raise Exception("Unsupported file format")
    except Exception as e:
        print(f"[CONVERT ERROR] {str(e)}")  # Log lỗi chi tiết
        return None

def convert_doc_to_docx(doc_path: Path) -> Union[Path, None]:
    try:
        if not pypandoc.get_pandoc_path():
            pypandoc.ensure_pandoc_installed()
            pypandoc.set_pandoc_path(PANDOC_PATH)
        pandoc_path = pypandoc.get_pandoc_path()
        if not pandoc_path or pandoc_path == "pandoc":
            return convert_doc_to_docx_with_libreoffice(doc_path)
        print(f"Using pandoc at: {pandoc_path}")  # Debug log
        output_path = Path(tempfile.gettempdir()) / (doc_path.stem + ".docx")
        print(f"Converting {doc_path} to {output_path}")  # Debug log
        pypandoc.convert_file(str(doc_path), 'docx', outputfile=str(output_path), extra_args=["--extract-media=."])
        print(f"Conversion to .docx completed, checking existence: {output_path.exists()}")  # Debug log
        return output_path if output_path.exists() else convert_doc_to_docx_with_libreoffice(doc_path)
    except Exception as e:
        print(f"[CONVERT ERROR] {str(e)}")
        return convert_doc_to_docx_with_libreoffice(doc_path)