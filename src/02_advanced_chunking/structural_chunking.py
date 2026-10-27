from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DOC_DIR = ROOT / "data" / "input" / "documents"

FALLBACK = """# NovaFlow
NovaFlow automates approvals and operational workflows.
## Deployment
Install the service in a private cloud.

Configure one workflow workspace per business unit. Restart workers after changing settings.
## Security
NovaSecure roles restrict workflow administration. Audit events are retained.
"""

def load_markdown() -> str:
    return FALLBACK

def structural_chunks(text: str, max_words: int = 28) -> list[dict]:
    """Create size-limited chunks that preserve headings.

    Args:
        text: Markdown text to split.
        max_words: Maximum words allowed in each chunk.

    Returns:
        Chunks with their section breadcrumbs.
    """    

    path: list[str] = []
    # Keeps a track of current heading hierarchy.
    # Example: ["Introduction", "RAG", "Chunking"]

    sections: list[tuple[str, list[str]]] = []
    # Stores completed sections as:
    # ("Introduction > RAG", ["paragraph1", "paragraph2"....])

    paragraphs: list[str] = []
    # Stores complete paragraph temporarily that belong to the current section.

    paragraph_lines: list[str] = []
    # Temporarily collects individual lines that together form one paragraph.

    def flush_paragraph():
        """Save collected lines as one paragraph."""
        if paragraph_lines:
            paragraphs.append(" ".join(paragraph_lines))
            paragraph_lines.clear()

    def flush_section():
        """Save the current section and clear its paragraphs."""
        flush_paragraph()

        if paragraphs:
            sections.append((" > ".join(path) or "Document", paragraphs.copy()))
            paragraphs.clear()

    for line in text.splitlines():

        if line.startswith("#"):
            flush_section()
            level = len(line) - len(line.strip("#"))
            # "### This is level 3"
            path[level - 1:] = [line[level:].strip()]

        elif not line.strip():
            flush_paragraph()

        elif line.strip():
            paragraph_lines.append(line.strip())

    flush_section()

    chunks = []

    for breadcrumb, paragraphs in sections:
        current: list[str] = []
        current_words = 0

        for paragraph in paragraphs:
            words = paragraph.split()

            # If a paragraph is larger than 'max_words', split it into smaller pieces of at most 'max_words' words.
            pieces = [" ".join(words[i: i + max_words])
                      for i in range(0, len(words), max_words)]
            for piece in pieces:
                piece_words = len(piece.split())

                if current and current_words + piece_words > max_words:
                    chunks.append({"section": breadcrumb, "text": "\n\n".join(current)})
                    current = []
                    current_words = 0
                
                current.append(piece)
                current_words += piece_words

        if current:
            chunks.append({"section": breadcrumb, "text": "\n\n".join(current)})

    return chunks

def main():
    text = load_markdown()
    chunks = structural_chunks(text)
    print(f"[parse] created {len(chunks)} heading-aware chunks.")
    for index, chunk in enumerate(chunks, 1):
        print(f"  {index}. section={chunk['section']}")
        print(f"     {chunk['text'][:110]}")

if __name__=="__main__":
    main()