from pypdf import PdfReader
import json
import sys
import argparse


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

reader = PdfReader("inputfiles/PIT2.pdf")
fields = reader.get_fields()

for name, info in (fields or {}).items():
    print(name, "=>", info.get("/FT"), info.get("/V"))

last_name = payload.get("lastName")
first_name = payload.get("firstName")
birth_date = payload.get("birthDate")
pesel = payload.get("pesel")
employer_name = payload.get("employerName")

print(f"Last Name: {last_name}")
print(f"First Name: {first_name}")
print(f"Birth Date: {birth_date}")
print(f"PESEL: {pesel}")
print(f"Employer Name: {employer_name}")