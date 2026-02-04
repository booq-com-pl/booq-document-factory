from pathlib import Path
import logging

log = logging.getLogger(__name__)



class BooqTemplateDocument:
    def __init__(self, templateDocument: str) -> None:
        self.templateDocument = templateDocument

        path = Path(templateDocument)
        self.documentPath = str(path.parent)    # location of the template
        self.documentName = path.stem           # name without suffix
        self.fullDocumentName = path.name       # name with suffix
        self.fullDocumentNameAndPath = str(path)  # full path with name and suffix
