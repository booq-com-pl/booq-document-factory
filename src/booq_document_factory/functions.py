import sys
from pathlib import Path
import json
import sys
import argparse
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject
from datetime import date
import shutil
import subprocess
import tempfile
from docxtpl import DocxTemplate
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler
import logging
log = logging.getLogger(__name__)



def setup_logging(
    *,
    level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = "app.log",
) -> None:
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(level)

    # usuń domyślne handlery, żeby nie dublować logów przy ponownym setupie
    logger.handlers.clear()

    # 1) Konsola – ładny output
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_path=False,
    )
    console_handler.setLevel(level)

    # 2) Plik – klasyczny format, łatwy do grep/analizy
    file_handler = RotatingFileHandler(
        Path(log_dir) / log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)

    file_formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

#-----

def load_config_toml(path: str | None = None) -> dict:
    try:
        import tomllib  # py311+
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("TOML requires Python 3.11+ (tomllib)") from exc

    config_path = Path(path) if path else Path("config.toml")
    if not config_path.exists():
        return {}

    raw = config_path.read_text(encoding="utf-8")
    return tomllib.loads(raw)

# -----

def doc_templates_list(templates_dir: str | Path = "src/booq_document_factory/templates") -> tuple[list[Path], list[Path]]:
    templates_path = Path(templates_dir)

    if not templates_path.exists():
        print(f"not found template directory: [{templates_path}]")
        return [], []

    pdfs: list[Path] = []
    docxs: list[Path] = []
    for path in templates_path.rglob("*"):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext == ".pdf":
            pdfs.append(path)
        elif ext == ".docx":
            docxs.append(path)

    return sorted(pdfs), sorted(docxs)

# -----

def createPdfDocument(_pdf_template, payload):
    reader = PdfReader(_pdf_template.documentPath + "/" + _pdf_template.fullDocumentName)
    fields = reader.get_fields() or {}

    log.info("PDF Form Fields:")
    for name, info in fields.items():
        # info is a field dictionary; /FT is field type, /V is current value
        try:
            print(name, "=>", info.get("/FT"), info.get("/V"))
        except Exception:
            log.info(name)

    last_name = payload.get("employeeLastName") or ""
    first_name = payload.get("employeeFirstName") or ""
    birth_date = payload.get("employeeBirthDate") or ""
    pesel = payload.get("employeePesel") or ""
    employer_name = payload.get("employerName") or ""

    # Output path
    out_dir = Path("outputfiles")
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_initial = first_name[0] if first_name else "_"
    artifact_name = out_dir / f"{_pdf_template.documentName}_{safe_initial}{last_name}.pdf"

    log.info(f"Last Name: {last_name}")
    log.info(f"First Name: {first_name}")
    log.info(f"Birth Date: {birth_date}")
    log.info(f"PESEL: {pesel}")
    log.info(f"Employer Name: {employer_name}")
    log.info(f"Output document: {artifact_name}")

    # Map of field name -> value (this is what pypdf expects)
    values = {
        "Text1": "A",
        "Text1.0.0": pesel,
        "Text1.1": "B",
        "Text1.1.0": "C",
        "Text1.1.0.0": last_name,
        "Text1.1.1": first_name,
        "Text1.0.1": "D",
        "Text1.0.1.0": "C",
        "Text1.0.1.1": "E",
        "Text1.0.1.1.0": "A",
        "Text1.0.1.1.1": "B",
        "Text15": "F",
        "Text15.0": "D",
        "Text15.1": "G",
        "Text15.1.0": "E",
        "Text15.1.1": "F",
        "Text17": "G",
        "Text18": "H",
        "Text19": "I",
        # "topmostSubform[0].Page1[0].DataUrodzenia[0]": birth_date,
        # "topmostSubform[0].Page1[0].DataWypelnienia[0]": date.today().isoformat(),
    }

    writer = PdfWriter(clone_from=reader)

    try:
        root = writer._root_object
        acro = root.get("/AcroForm")
        if not acro:
            log.error("No /AcroForm dictionary found. Skipping form field update, skipping document generation.")
            with open(artifact_name, "wb") as output_pdf:
                writer.write(output_pdf)
            return

        acro_obj = acro.get_object()
        acro_obj.update({NameObject("/NeedAppearances"): BooleanObject(True)})
        if "/XFA" in acro_obj:
            print("Warning: XFA detected in /AcroForm. Removing /XFA so AcroForm values are used.")
            del acro_obj[NameObject("/XFA")]
    except Exception as e:
        print(f"Warning: couldn't adjust AcroForm/XFA: {e}")

    try:
        writer.update_page_form_field_values(None, values, auto_regenerate=True)
    except TypeError:
        for page in writer.pages:
            writer.update_page_form_field_values(page, values)

    with open(artifact_name, "wb") as output_pdf:
        writer.write(output_pdf)

#-----

def createWordDocument(_docx_template, payload):

    out_dir = Path("outputfiles")
    out_dir.mkdir(parents=True, exist_ok=True)

    last_name = payload.get("employeeLastName") or ""
    first_name = payload.get("employeeFirstName") or ""
    safe_initial = first_name[0] if first_name else "_"
    base_name = out_dir / f"{_docx_template.documentName}_{safe_initial}{last_name}"

    log.info(f"Rendering DOCX from template: {_docx_template.fullDocumentNameAndPath}")
    try:
        docx_path, pdf_path = render_docx_and_convert(_docx_template.fullDocumentNameAndPath, payload, base_name)
        log.info(f"Saved DOCX: {docx_path}")
        log.info(f"Saved PDF: {pdf_path}")
    except Exception as e:
        log.error(f"Error creating DOCX/PDF: {e}")

#-----

def convert_docx_to_pdf(docx_path: Path, out_dir: Path) -> Path:
    """Convert a .docx file to PDF using headless LibreOffice and return the PDF path."""
    # Ensure LibreOffice is available
    if shutil.which("soffice") is None:
        raise FileNotFoundError(
            "LibreOffice 'soffice' not found in PATH. Install it in your environment "
            "(Ubuntu: 'sudo apt-get update && sudo apt-get install -y libreoffice'; "
            "macOS: 'brew install --cask libreoffice')."
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "soffice",
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to",
        "pdf",
        "--outdir",
        str(out_dir),
        str(docx_path),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"LibreOffice conversion failed: {p.stderr or p.stdout}")

    pdf_path = out_dir / (docx_path.stem + ".pdf")
    if not pdf_path.exists():
        raise RuntimeError("PDF was not created.")
    return pdf_path

#-----

def render_docx_and_convert(template_path: str | Path, payload: dict, output_path: str | Path) -> tuple[Path, Path]:
    """Render a DOCX template with `payload` and convert to PDF.

    - `template_path` must point to an existing .docx template file.
    - `output_path` is the base path (without suffix) where .docx and .pdf will be saved.

    Returns tuple (saved_docx_path, saved_pdf_path).
    """
    template_path = Path(template_path)
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    if template_path.suffix.lower() != ".docx":
        raise ValueError("template_path must be a .docx file")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        in_docx = td / "template.docx"
        rendered_docx = td / "rendered.docx"
        pdf_out_dir = td / "pdf"

        # Copy template into temp dir
        log.info(f"Copying template [{template_path.name}] to temp dir: {in_docx}")
        shutil.copy2(template_path, in_docx)


        # Render DOCX
        log.info(f"Rendering DOCX to: {rendered_docx}")
        try:
            doc = DocxTemplate(str(in_docx))
            doc.render(payload)
            doc.save(str(rendered_docx))
            log.info(f"DOCX rendered and saved to: {rendered_docx}")
        except Exception as e:
            raise RuntimeError(f"DOCX render failed: {e}")

        # Verify the rendered DOCX was saved
        if not rendered_docx.exists():
            raise RuntimeError(f"Rendered DOCX file was not saved: {rendered_docx}")

        log.info(f"Verified DOCX file saved successfully: {rendered_docx}")

        # Convert to PDF
        pdf_path = convert_docx_to_pdf(rendered_docx, pdf_out_dir)

        # Move to final destination
        target_docx = output_path.with_suffix(".docx")
        target_pdf = output_path.with_suffix(".pdf")
        log.info(f"Copying rendered DOCX and PDF to output path: {output_path}.docx")
        shutil.copy2(rendered_docx, target_docx)
        shutil.copy2(pdf_path, target_pdf)

    return target_docx, target_pdf
