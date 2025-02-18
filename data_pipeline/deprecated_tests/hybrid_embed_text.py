import json

from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

DOC_SOURCE = "./data/raw/FAQs.md"

converter = DocumentConverter()
doc = converter.convert(source=DOC_SOURCE).document

# model based context aware chunking with hierarchy in mind
chunker = HybridChunker(max_tokens=200)

chunks = chunker.chunk(doc)

# store text and embeddings
chunk_data = []
for idx, chunk in enumerate(chunks):
    chunk_text = chunk.text.strip()
    embedding = embedding_model.encode(chunk_text).tolist()  # Convert NumPy array to list

    chunk_data.append({
        "chunk_id": idx + 1,
        "text": chunk_text,
        "embedding": embedding
    })

# Save to JSON file
output_file = "./data/serialized_chunks.json"
with open(output_file, "w") as file:
    json.dump(chunk_data, file, indent=4)

    

print(f"Serialized {len(chunk_data)} chunks with embeddings to {output_file}")