import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct

# Load the Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose a different model if needed

# Initialize the Qdrant client
client = QdrantClient(url="http://localhost:6333")

# Define your collection name
collection_name = "your_collection_name"

# Check if the collection exists, if not, create it
if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance="Cosine")  # Adjust size based on the model
    )

# Read data from CSV
data = pd.read_csv('your_data.csv')  # Replace with your CSV file path

# Prepare points for Qdrant
points = []
for idx, row in data.iterrows():
    section_text = row['section']  # Adjust based on your CSV column name
    vector = model.encode(section_text).tolist()  # Generate vector using Sentence Transformer
    payload = {
        "state": row["state"],
        "year": row["year"],
        "title": row["title"],
        "chapter": row["chapter"],
        "article": row["article"]
    }
    points.append(PointStruct(id=idx + 1, vector=vector, payload=payload))

# Upload points to Qdrant
operation_info = client.upsert(
    collection_name=collection_name,
    wait=True,
    points=points
)

print("Data uploaded successfully:", operation_info)
