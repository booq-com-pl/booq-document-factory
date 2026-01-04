from pypdf import PdfReader

reader = PdfReader("inputfiles/PIT2.pdf")

fields = reader.get_fields()

for name, info in (fields or {}).items():
    print(name, "=>", info.get("/FT"), info.get("/V"))
