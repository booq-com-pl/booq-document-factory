from pathlib import Path


class BooqTemplateDocument:
    def __init__(self, templateDocument: str) -> None:
        self.templateDocument = templateDocument

        path = Path(templateDocument)
        self.documentPath = str(path.parent)
        self.documentName = path.stem
        self.fullDocumentName = path.name
