import os
import uuid

from typing import List, Dict, Any, Optional
from qdrant_client import AsyncQdrantClient, models
from fastembed import TextEmbedding, SparseTextEmbedding

class QdrantDB:
    def __init__(self):
        # 1. Configuration
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        print(f"Connecting to Qdrant at: {self.qdrant_url}")
        
        # Use Async Client for FastAPI efficiency
        self.client = AsyncQdrantClient(url=self.qdrant_url)
        
        # Collections
        self.DRAFTS_COLLECTION = "email_drafts"
        self.NOTES_COLLECTION = "user_notes"
        
        # 2. Load AI Models (FastEmbed)
        print("Loading Hybrid Models (Dense + Sparse)...")
        # Dense for Semantic Search (Meaning)
        self.dense_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        # Sparse for Keyword Search (Exact Match)
        self.sparse_model = SparseTextEmbedding(model_name="prithivida/Splade_PP_en_v1")
        
    async def init_collections(self):
        """Creates collections with Hybrid (Dense + Sparse) config."""
        for col in [self.DRAFTS_COLLECTION, self.NOTES_COLLECTION]:
            if not await self.client.collection_exists(col):
                await self.client.create_collection(
                    collection_name=col,
                    vectors_config={
                        "dense": models.VectorParams(
                            size=384,
                            distance=models.Distance.COSINE
                        )
                    },
                    sparse_vectors_config={
                        "sparse": models.SparseVectorParams(
                            index=models.SparseIndexParams(on_disk=True)
                        )
                    }
                )
                print(f"Created Hybrid Collection: {col}")

    # --- EMBEDDING HELPERS ---
    def _get_dense_embedding(self, text: str) -> List[float]:
        # list() consumes the generator
        return list(self.dense_model.embed([text]))[0].tolist()

    def _get_sparse_embedding(self, text: str) -> models.SparseVector:
        sparse_vec = list(self.sparse_model.embed([text]))[0]
        return models.SparseVector(
            indices=sparse_vec.indices.tolist(),
            values=sparse_vec.values.tolist()
        )

    # --- GENERIC UPSERT/SEARCH ---
    async def _upsert(self, collection_name: str, point_id: str, text: str, payload: Dict[str, Any]):
        """
        Generates both Dense and Sparse vectors and uploads them.
        """
        dense_vec = self._get_dense_embedding(text)
        sparse_vec = self._get_sparse_embedding(text)
        
        await self.client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id, 
                    vector={
                        "dense": dense_vec, 
                        "sparse": sparse_vec
                    }, 
                    payload=payload
                )
            ]
        )

    async def _search(self, collection_name: str, user_id: int, query_text: str, limit: int) -> List[Dict[str, Any]]:
        """
        Performs Hybrid Search using RRF (Reciprocal Rank Fusion).
        """
        dense_query = self._get_dense_embedding(query_text)
        sparse_query = self._get_sparse_embedding(query_text)
        
        # Filter by User ID for security
        user_filter = models.Filter(
            must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
        )

        results = await self.client.query_points(
            collection_name=collection_name,
            prefetch=[
                models.Prefetch(
                    query=sparse_query, 
                    using="sparse", 
                    filter=user_filter, 
                    limit=limit * 2
                ),
                models.Prefetch(
                    query=dense_query, 
                    using="dense", 
                    filter=user_filter, 
                    limit=limit * 2
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit
        )

        # Parse results
        matches: List[Dict[str, Any]] = []
        for hit in results.points:
            # Safe payload extraction
            payload = hit.payload if hit.payload else {}
            matches.append({
                "id": hit.id,
                "score": hit.score,
                **payload
            })
        return matches
    
    async def _delete(self, collection_name: str, point_id: str):
        await self.client.delete(
            collection_name=collection_name, 
            points_selector=models.PointIdsList(points=[point_id])
        )

    # --- PUBLIC METHODS FOR ROUTERS ---
    
    async def upsert_draft(self, user_id: int, draft_data: Dict[str, Any], draft_id: Optional[str] = None) -> str:
        """Saves or updates an email draft."""
        point_id = draft_id if draft_id else str(uuid.uuid4())
        
        # Combine subject and body for search
        search_text = f"{draft_data.get('subject', '')} {draft_data.get('body', '')}"
        
        payload: Dict[str, Any] = {
            "user_id": user_id,
            "subject": draft_data.get("subject"),
            "body": draft_data.get("body"),
            "to_email": draft_data.get("to_email"),
            "recipient_name": draft_data.get("recipient_name"),
            "status": "draft"
        }
        
        await self._upsert(self.DRAFTS_COLLECTION, point_id, search_text, payload)
        return point_id

    async def search_drafts(self, user_id: int, query: str, limit: int = 10):
        return await self._search(self.DRAFTS_COLLECTION, user_id, query, limit)

    # --- UPDATED METHOD HERE ---
    async def upsert_note(self, user_id: int, content: str, note_id: Optional[str] = None) -> str:
        """Saves (creates) or updates a user note."""
        # If note_id is provided, use it (Update); otherwise generate new UUID (Create)
        point_id = note_id if note_id else str(uuid.uuid4())
        
        payload: Dict[str, Any] = {
            "user_id": user_id,
            "content": content,
            "type": "note"
        }
        await self._upsert(self.NOTES_COLLECTION, point_id, content, payload)
        return point_id

    async def search_notes(self, user_id: int, query: str, limit: int = 10):
        return await self._search(self.NOTES_COLLECTION, user_id, query, limit)

    async def delete_note(self, note_id: str):
        """Public method to delete a note."""
        await self._delete(self.NOTES_COLLECTION, note_id)
        
    async def delete_draft(self, draft_id: str):
        """Public method to delete a draft."""
        await self._delete(self.DRAFTS_COLLECTION, draft_id)

    async def list_all_notes(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves the latest notes for a user (Pagination can be added later).
        """
        # Filter by user_id
        user_filter = models.Filter(
            must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
        )

        # Scroll: reads points directly from storage
        results, _ = await self.client.scroll(
            collection_name=self.NOTES_COLLECTION,
            scroll_filter=user_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        return [{
            "id": point.id,
            **(point.payload or {})  # SAFE UNPACKING
        } for point in results]

    async def list_all_drafts(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves all drafts for a user.
        """
        user_filter = models.Filter(
            must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
        )

        results, _ = await self.client.scroll(
            collection_name=self.DRAFTS_COLLECTION,
            scroll_filter=user_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        return [{
            "id": point.id,
            **(point.payload or {}) # SAFE UNPACKING
        } for point in results]

# Singleton Instance
vector_db = QdrantDB()