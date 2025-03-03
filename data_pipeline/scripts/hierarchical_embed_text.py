import json
from docling.document_converter import DocumentConverter
from docling.chunking import HierarchicalChunker
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Path to your FAQ document
DOC_SOURCE = "./data/raw/FAQs.md"

# Convert the document
converter = DocumentConverter()
doc = converter.convert(source=DOC_SOURCE).document

# Initialize the HierarchicalChunker
chunker = HierarchicalChunker()

# Chunk the document
chunks = list(chunker.chunk(doc))

# Process and embed each chunk
chunk_data = []
for i in range(0, len(chunks), 2):
    chunk_text = chunks[i].text.strip()
    if i + 1 < len(chunks):
        chunk_text += "\n\n" + chunks[i+1].text.strip()
    
    if chunk_text:  # Ensure the chunk is not empty
        embedding = embedding_model.encode(chunk_text).tolist()
        chunk_data.append({
            "chunk_id": (i/2)+1,
            "text": chunk_text,
            "embedding": embedding
        })

# Save the processed chunks to a JSON file
output_file = "./data/hierarchical_serialized_chunks.json"
with open(output_file, "w") as file:
    json.dump(chunk_data, file, indent=4)

print(f"Serialized {len(chunk_data)} QA chunks to {output_file}")
