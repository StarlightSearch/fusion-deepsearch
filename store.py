import os
from typing import List
import requests
from urllib.parse import urlparse
import lancedb
import embed_anything
from embed_anything import EmbeddingModel, WhichModel, ONNXModel , TextEmbedConfig
from uuid import uuid4



class VectorStore:

    def __init__(self, directory, **kwargs):
        super().__init__(**kwargs)
        self.config = TextEmbedConfig(chunk_size=1000, batch_size=32)
        self.model = EmbeddingModel.from_pretrained_onnx(WhichModel.Bert, ONNXModel.AllMiniLML6V2Q)
        self.connection = lancedb.connect("tmp/general1")
        if "docs" in self.connection.table_names():
            self.table = self.connection.open_table("docs")
        else:
            self.embeddings = embed_anything.embed_directory(directory, embedder = self.model, config=self.config)
            docs = []
            for e in self.embeddings:
                docs.append({
                    "vector": e.embedding,
                    "text": e.text,
                    "file_name": e.metadata["file_name"],
                    "id": str(uuid4())
                })
            self.table = self.connection.create_table("docs", docs)

    def forward(self, query: str) -> List[str]:
        assert isinstance(query, str)

        query_vec = embed_anything.embed_query([query], embedder=self.model)[0].embedding
        docs = self.table.search(query_vec).limit(5).to_pandas()
        output = []
        for _, row in docs.iterrows():
            context = f"File Name: {row['file_name']} \n Text: {row['text']}"
            output.append(context)
        return output
    # "\nRetrieved documents:\n" + "".join(
    #         [f"\n\n===== Document {str(i)} =====\n" + doc for i, doc in enumerate(docs)]
    #     )
    
if __name__ == "__main__":
    store = VectorStore("doc") 
    print(list(store.forward("What is attention?")))