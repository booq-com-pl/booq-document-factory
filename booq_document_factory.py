import json
import sys
import argparse
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject
from pathlib import Path
from datetime import date


def load_payload():
    parser = argparse.ArgumentParser(description="Create custom documents from JSON payload")
    parser.add_argument("payload", nargs="?", help="JSON payload string (positional) or use --payload")
    parser.add_argument("--payload", dest="payload_flag", help="JSON payload string (flag)")
    args = parser.parse_args()

    payload_str = args.payload_flag or args.payload
    if not payload_str:
        print("Error: payload missing. Provide JSON as positional arg or via --payload.")
        sys.exit(2)

    try:
        return json.loads(payload_str)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON payload: {e}")
        sys.exit(2)


payload = load_payload()

def create_pit2():
    reader = PdfReader("inputfiles/PIT2.pdf")
    fields = reader.get_fields() or {}

    print("PDF Form Fields:")
    for name, info in fields.items():
        # info is a field dictionary; /FT is field type, /V is current value
        try:
            print(name, "=>", info.get("/FT"), info.get("/V"))
        except Exception:
            print(name)

    last_name = payload.get("lastName") or ""
    first_name = payload.get("firstName") or ""
    birth_date = payload.get("birthDate") or ""
    pesel = payload.get("pesel") or ""
    employer_name = payload.get("employerName") or ""

    # Output path
    out_dir = Path("outputfiles")
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_initial = first_name[0] if first_name else "_"
    artifact_name = out_dir / f"PIT2_{safe_initial}{last_name}.pdf"

    print(f"Last Name: {last_name}")
    print(f"First Name: {first_name}")
    print(f"Birth Date: {birth_date}")
    print(f"PESEL: {pesel}")
    print(f"Employer Name: {employer_name}")
    print(f"Creating document: {artifact_name}")

    # Map of field name -> value (this is what pypdf expects)
    values = {
        "topmostSubform[0].Page1[0].PESEL1[0]": pesel,
        "topmostSubform[0].Page1[0].Nazwisko[0]": last_name,
        "topmostSubform[0].Page1[0].Imie[0]": first_name,
        "topmostSubform[0].Page1[0].Zaklad[0]": employer_name,
        "topmostSubform[0].Page1[0].DataUrodzenia[0]": birth_date,
        "topmostSubform[0].Page1[0].DataWypelnienia[0]": date.today().isoformat(),
    }

    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # Copy AcroForm from source PDF (important for form PDFs)
    try:
        root = reader.trailer.get("/Root", {})
        acroform = root.get("/AcroForm")
        if acroform:
            writer._root_object.update({NameObject("/AcroForm"): acroform})
            # Many viewers need NeedAppearances to be true to show updated values.
            try:
                writer._root_object["/AcroForm"].update({NameObject("/NeedAppearances"): BooleanObject(True)})
            except Exception:
                pass
    except Exception as e:
        print(f"Warning: couldn't copy AcroForm from source PDF: {e}")

    # Fill values on all pages (safe even if fields are on page 1)
    for page in writer.pages:
        writer.update_page_form_field_values(page, values)

    with open(artifact_name, "wb") as output_pdf:
        writer.write(output_pdf)

    print(f"Saved filled PDF: {artifact_name}")


create_pit2()