import sys
import argparse
from booq_document_factory import functions as booq
from booq_document_factory.classes import BooqTemplateDocument
import logging

log = logging.getLogger(__name__)

def main() -> int:

    booq.setup_logging(level="INFO")
    log.info("Start")

    parser = argparse.ArgumentParser(description="Create custom documents from JSON payload")
    parser.add_argument("payload", nargs="?", help="JSON payload string (positional) or use --payload")
    parser.add_argument("--payload", dest="payload_flag", help="JSON payload string (flag)")
    args = parser.parse_args()

    payload_str = args.payload_flag or args.payload
    if not payload_str:
        log.exception("Error: payload missing. Provide JSON as positional arg or via --payload.")
        sys.exit(2)

    CONFIG = booq.load_config_toml()

    SPLIBRARY = (CONFIG.get("splibrary") or {})
    url = SPLIBRARY.get("url")
    if url:
        log.info(f"SharePoint library URL: {url}")
    else:
        log.exception("SharePoint library URL not configured.")


    log.info(payload_str)

    pdf_templates, docx_templates = booq.doc_templates_list()

    for pdf_template in pdf_templates:
        log.info(f"Processing PDF template: {pdf_template}")
        _pdf_template = BooqTemplateDocument(str(pdf_template))
        log.info(f"Template document name: {_pdf_template.documentName}")
        log.info(f"Template document path: {_pdf_template.documentPath}")
        log.info(f"Full template document name: {_pdf_template.fullDocumentName}")

    for docx_template in docx_templates:
        log.info(f"Processing DOCX template: {docx_template}")
        _docx_template = BooqTemplateDocument(str(docx_template))
        log.info(f"Template document name: {_docx_template.documentName}")
        log.info(f"Template document path: {_docx_template.documentPath}")
        log.info(f"Full template document name: {_docx_template.fullDocumentName}")

    # log.info(f"PDF templates: {pdf_templates}")

    # log.info(f"DOCX templates: {docx_templates}")
    # booq.create_pit2(payload_str)

    # booq.create_docx(payload_str)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
