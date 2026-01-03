"""
FastAPI Backend for IPC/BNS Legal Reasoning Agent
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import uvicorn

from database import init_db, get_db, IPCBNSMapping, LandmarkCase, AnalysisHistory
from rag_system import CaseLawRAG
from legal_agent import LegalReasoningAgent

# Initialize FastAPI app
app = FastAPI(
    title="IPC/BNS Legal Reasoning Agent",
    description="AI-powered legal analysis system for IPC to BNS transition",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and RAG system at startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG system"""
    from ipc_bns_data import LANDMARK_CASES

    engine, SessionLocal = init_db()
    app.state.SessionLocal = SessionLocal

    # Initialize RAG system
    print("Initializing RAG system for case search...")
    app.state.rag = CaseLawRAG()

    # Check if RAG collection is empty and populate if needed
    try:
        count = app.state.rag.collection.count()
        if count == 0:
            print(f"RAG collection empty. Adding {len(LANDMARK_CASES)} cases...")
            app.state.rag.add_cases(LANDMARK_CASES)
            print(f"✓ Added {len(LANDMARK_CASES)} cases to RAG system")
        else:
            print(f"✓ RAG system already has {count} cases indexed")
    except Exception as e:
        print(f"Warning: Could not check RAG collection: {e}")
        print(f"Initializing with {len(LANDMARK_CASES)} cases...")
        app.state.rag.add_cases(LANDMARK_CASES)

    print("✓ Database and RAG system initialized")


# Pydantic models for API
class SectionQuery(BaseModel):
    ipc_section: str


class MultiSectionQuery(BaseModel):
    ipc_sections: List[str]
    context: Optional[str] = ""


class MemoRequest(BaseModel):
    ipc_sections: List[str]
    query_context: Optional[str] = ""


class CaseSearchQuery(BaseModel):
    query: str
    n_results: Optional[int] = 5


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "IPC/BNS Legal Reasoning Agent API",
        "version": "1.0.0",
        "endpoints": {
            "/sections": "List all IPC sections",
            "/section/{ipc_section}": "Get details for specific IPC section",
            "/analyze": "Analyze IPC to BNS transition",
            "/memo": "Generate legal memorandum",
            "/cases/search": "Search case law",
            "/cases": "List all landmark cases"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/sections")
async def list_sections(
    category: Optional[str] = None,
    has_changes: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all IPC sections with optional filtering"""
    query = db.query(IPCBNSMapping)

    if category:
        query = query.filter(IPCBNSMapping.category == category)

    if has_changes is not None:
        query = query.filter(IPCBNSMapping.has_changes == has_changes)

    sections = query.all()

    return {
        "total": len(sections),
        "sections": [
            {
                "ipc_section": s.ipc_section,
                "ipc_description": s.ipc_description,
                "bns_section": s.bns_section,
                "bns_description": s.bns_description,
                "category": s.category,
                "has_changes": s.has_changes,
                "change_type": s.change_type
            }
            for s in sections
        ]
    }


@app.get("/section/{ipc_section}")
async def get_section(ipc_section: str, db: Session = Depends(get_db)):
    """Get detailed information for a specific IPC section"""
    section = db.query(IPCBNSMapping).filter(
        IPCBNSMapping.ipc_section == ipc_section
    ).first()

    if not section:
        raise HTTPException(status_code=404, detail=f"IPC Section {ipc_section} not found")

    # Get associated cases
    cases = [
        {
            "case_name": case.case_name,
            "citation": case.citation,
            "year": case.year,
            "court": case.court
        }
        for case in section.cases
    ]

    return {
        "ipc_section": section.ipc_section,
        "ipc_description": section.ipc_description,
        "ipc_text": section.ipc_text,
        "bns_section": section.bns_section,
        "bns_description": section.bns_description,
        "bns_text": section.bns_text,
        "category": section.category,
        "punishment": section.punishment,
        "has_changes": section.has_changes,
        "change_type": section.change_type,
        "change_summary": section.change_summary,
        "landmark_cases": cases
    }


@app.post("/analyze")
async def analyze_transition(request: SectionQuery, db: Session = Depends(get_db)):
    """Analyze IPC to BNS transition for a section"""
    rag = app.state.rag
    agent = LegalReasoningAgent(db, rag)

    analysis = agent.analyze_section_transition(request.ipc_section)

    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])

    return analysis


@app.post("/memo")
async def generate_memo(request: MemoRequest, db: Session = Depends(get_db)):
    """Generate comprehensive legal memorandum"""
    rag = app.state.rag
    agent = LegalReasoningAgent(db, rag)

    memo = agent.generate_legal_memo(
        request.ipc_sections,
        request.query_context
    )

    # Save to history
    history = AnalysisHistory(
        query=request.query_context,
        ipc_sections=str(request.ipc_sections),
        memo_generated=memo
    )
    db.add(history)
    db.commit()

    return {
        "memo": memo,
        "sections_analyzed": request.ipc_sections,
        "generated_at": history.created_at.isoformat()
    }


@app.post("/cases/search")
async def search_cases(request: CaseSearchQuery):
    """Search case law using semantic search"""
    rag = app.state.rag
    results = rag.search_cases(request.query, n_results=request.n_results)

    return {
        "query": request.query,
        "results": results
    }


@app.get("/cases")
async def list_cases(
    year: Optional[int] = None,
    court: Optional[str] = None,
    validity_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all landmark cases with optional filtering"""
    query = db.query(LandmarkCase)

    if year:
        query = query.filter(LandmarkCase.year == year)

    if court:
        query = query.filter(LandmarkCase.court.ilike(f"%{court}%"))

    if validity_status:
        query = query.filter(LandmarkCase.validity_status == validity_status)

    cases = query.all()

    return {
        "total": len(cases),
        "cases": [
            {
                "id": case.id,
                "case_name": case.case_name,
                "citation": case.citation,
                "court": case.court,
                "year": case.year,
                "validity_status": case.validity_status
            }
            for case in cases
        ]
    }


@app.get("/cases/{case_id}")
async def get_case(case_id: int, db: Session = Depends(get_db)):
    """Get full details of a specific case"""
    case = db.query(LandmarkCase).filter(LandmarkCase.id == case_id).first()

    if not case:
        raise HTTPException(status_code=404, detail=f"Case ID {case_id} not found")

    return {
        "case_name": case.case_name,
        "citation": case.citation,
        "court": case.court,
        "year": case.year,
        "judges": case.judges,
        "facts": case.facts,
        "legal_issues": case.legal_issues,
        "judgment_summary": case.judgment_summary,
        "ratio_decidendi": case.ratio_decidendi,
        "obiter_dicta": case.obiter_dicta,
        "validity_status": case.validity_status,
        "validity_reasoning": case.validity_reasoning,
        "related_sections": [
            {
                "ipc_section": section.ipc_section,
                "bns_section": section.bns_section
            }
            for section in case.sections
        ]
    }


@app.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get database statistics"""
    total_sections = db.query(IPCBNSMapping).count()
    sections_with_changes = db.query(IPCBNSMapping).filter(
        IPCBNSMapping.has_changes == True
    ).count()
    repealed_sections = db.query(IPCBNSMapping).filter(
        IPCBNSMapping.change_type == "repealed"
    ).count()
    total_cases = db.query(LandmarkCase).count()

    return {
        "total_ipc_sections": total_sections,
        "sections_with_changes": sections_with_changes,
        "repealed_sections": repealed_sections,
        "total_landmark_cases": total_cases,
        "change_rate": f"{(sections_with_changes/total_sections*100):.1f}%" if total_sections > 0 else "0%"
    }


@app.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of all categories"""
    categories = db.query(IPCBNSMapping.category).distinct().all()
    return {
        "categories": [cat[0] for cat in categories if cat[0]]
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
