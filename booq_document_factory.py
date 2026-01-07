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

    # Build writer by cloning the source PDF so all AcroForm references stay valid.
    # Copying /AcroForm manually often results in fields not being readable in the output.
    writer = PdfWriter(clone_from=reader)

    # Ensure values are visible in many viewers.
    # If this is a hybrid XFA PDF, remove /XFA so readers prefer AcroForm.
    try:
        root = writer._root_object
        acro = root.get("/AcroForm")
        if acro:
            acro_obj = acro.get_object()
            acro_obj.update({NameObject("/NeedAppearances"): BooleanObject(True)})
            if "/XFA" in acro_obj:
                print("Warning: XFA detected in /AcroForm. Removing /XFA so AcroForm values are used.")
                del acro_obj[NameObject("/XFA")]
    except Exception as e:
        print(f"Warning: couldn't adjust AcroForm/XFA: {e}")

    # Fill values. Prefer the document-level call if available; fall back to per-page.
    try:
        writer.update_page_form_field_values(None, values, auto_regenerate=True)
    except TypeError:
        for page in writer.pages:
            writer.update_page_form_field_values(page, values)

    with open(artifact_name, "wb") as output_pdf:
        writer.write(output_pdf)

    print(f"Saved filled PDF: {artifact_name}")

    print("verification")
    r = PdfReader(str(artifact_name))
    out_fields = r.get_fields() or {}
    print("output fields count:", len(out_fields))
    for k, v in out_fields.items():
        if any(s in k for s in ("PESEL", "Nazwisko", "Imie", "Zaklad", "Data")):
            print(k, "=>", v.get("/V"))

    if not out_fields:
        print("No AcroForm fields found in output; dumping page[0] annotations (/T => /V):")
        annots = r.pages[0].get("/Annots") or []
        for a in annots:
            try:
                obj = a.get_object()
                t = obj.get("/T")
                v = obj.get("/V")
                if t or v:
                    print(t, "=>", v)
            except Exception:
                pass


create_pit2()
