from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Document:
    id: str = field(default="")
    content: Optional[str] = field(default=None)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Chunker:
    def chunk(self, text: str, metadata: Dict[str:Any] = None, overlap: int = 0):
        for i in range(len(text) - overlap + 1):
            doc = Document()
            doc.id = i
            doc.content = text[i : i + overlap]
            doc.metadata = metadata if metadata else {}
            yield doc
