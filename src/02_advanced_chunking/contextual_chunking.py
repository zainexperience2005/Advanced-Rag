from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DOC_DIR = ROOT / "data" / "input" / "documents"
FALLBACK = """# NovaFlow Administration
## Synchronization
It runs every fifteen minutes by default.
Administrators can trigger it manually after a policy update.
## Access Control
NovaSecure supports reviewer, owner, and administrator roles.
"""


def load_markdown() -> tuple[str, str]:
    return FALLBACK, "TechNova NovaFlow Guide"

def contextualize(text: str, title: str) -> list[dict]:
    """Add document and section context to text chunks.

    Args:
        text: Markdown text to split into chunks.
        title: Title used as document context.

    Returns:
        Original chunks paired with context-rich text.
    """
    
    section = "Overview"
    chunks = []

    for line in text.splitlines():

        if line.startswith("#"):
            section = line.lstrip("#").strip()

        elif line.strip():
            context = f"Document: {title}. Section: {section}"
            chunks.append({"original": line.strip(), "embedding_text": f"{context} {line.strip()}"})

    return chunks


def score(query: str, text: str) -> int:
    """Count meaningful words shared by a query and text.

    Args:
        query: Search question to compare.
        text: Candidate text to score.

    Returns:
        Number of matching words.
    """    
    query_words = set(re.findall(r"[a-z]{3, }", query.lower()))
    return len(query_words & set(re.findall(r"[a-z]{3, }", text.lower())))

def main():
    text, title = load_markdown()
    chunks = contextualize(text, title)
    query = "Which NovaSecure access control roles are supported?"

    plain = max(chunks, key = lambda item: score(query, item["original"]))
    enriched = max(chunks, key = lambda item: score(query, item["embedding_text"]))
    
    print(f"[build] contextualized {len(chunks)} chunks")
    print(f"[query] -> {query}")
    print(f"[plain score] -> {score(query, plain['original'])}: {plain['original']}")
    print(f"[context score] {score(query, enriched['embedding_text'])}: {enriched['embedding_text']}")

if __name__=="__main__":
    main()