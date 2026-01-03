"""
RAG (Retrieval Augmented Generation) System for Case Law
Uses ChromaDB for vector storage and retrieval
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import json


class CaseLawRAG:
    def __init__(self, persist_directory="./chroma_db"):
        """Initialize RAG system with ChromaDB and embedding model"""
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        # Use sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Create or get collection
        try:
            self.collection = self.client.get_collection("case_law")
        except:
            self.collection = self.client.create_collection(
                name="case_law",
                metadata={"hnsw:space": "cosine"}
            )

    def add_cases(self, cases: List[Dict[str, Any]]):
        """Add landmark cases to vector database"""
        documents = []
        metadatas = []
        ids = []

        for i, case in enumerate(cases):
            # Create comprehensive document text for embedding
            doc_text = f"""
            Case: {case['case_name']}
            Citation: {case['citation']}
            Court: {case['court']}
            Year: {case['year']}

            Facts: {case['facts']}

            Legal Issues: {case['legal_issues']}

            Judgment: {case['judgment_summary']}

            Ratio Decidendi: {case['ratio_decidendi']}

            Obiter Dicta: {case.get('obiter_dicta', '')}

            IPC Sections: {', '.join(case['ipc_sections'])}

            Validity Status: {case['validity_status']}
            Validity Reasoning: {case.get('validity_reasoning', '')}
            """

            documents.append(doc_text)

            metadata = {
                "case_name": case['case_name'],
                "citation": case['citation'],
                "court": case['court'],
                "year": case['year'],
                "ipc_sections": json.dumps(case['ipc_sections']),
                "validity_status": case['validity_status']
            }
            metadatas.append(metadata)
            ids.append(f"case_{i}_{case['citation'].replace(' ', '_')}")

        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Added {len(cases)} cases to vector database")

    def search_cases(self, query: str, n_results: int = 5,
                     filter_sections: List[str] = None) -> List[Dict[str, Any]]:
        """Search for relevant cases using semantic search"""

        # Build where clause for filtering
        where_clause = None
        if filter_sections:
            # This is simplified - in production, you'd want more sophisticated filtering
            where_clause = {"validity_status": {"$ne": "invalid"}}

        # Perform semantic search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )

        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                result = {
                    "document": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                }
                formatted_results.append(result)

        return formatted_results

    def search_by_section(self, section: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search cases by IPC section number"""
        query = f"IPC Section {section} legal principles precedents"
        return self.search_cases(query, n_results=n_results)

    def get_all_cases_for_section(self, section: str) -> List[str]:
        """Get all case citations for a specific section"""
        # This would query the database for exact matches
        results = self.collection.get()

        relevant_cases = []
        if results['metadatas']:
            for metadata in results['metadatas']:
                sections = json.loads(metadata.get('ipc_sections', '[]'))
                if section in sections:
                    relevant_cases.append(metadata['citation'])

        return relevant_cases
