# IPC/BNS Legal Reasoning Agent - Usage Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Using the Web Interface](#using-the-web-interface)
3. [API Usage](#api-usage)
4. [Common Workflows](#common-workflows)
5. [Tips & Best Practices](#tips--best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Starting the Application

**Using Docker (Recommended):**

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Manual Start:**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
cd app
python -m uvicorn main:app --reload
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

### Accessing the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

---

## Using the Web Interface

### 1. Dashboard

The dashboard provides an overview of the system:

- **Statistics**: Total sections, changes, landmark cases
- **Feature Overview**: Key capabilities
- **Change Rate Analysis**: Visual representation of IPC→BNS changes

**Use Case**: Start here to understand the scope of the database.

---

### 2. Section Analyzer

Analyze individual IPC sections and their BNS equivalents.

**Steps:**

1. Navigate to "Section Analyzer" from the menu
2. Enter an IPC section number (e.g., `302`, `420`, `124A`)
3. Click "Analyze"

**Output Includes:**

- **IPC Section Details**: Description, text, category, punishment
- **BNS Equivalent**: Corresponding BNS section and text
- **Doctrinal Changes**: Type, severity, summary
- **Legal Implications**: Impact assessment
- **Validity Warnings**: Flags for precedent applicability
- **Landmark Cases**: Relevant Supreme Court cases with validity status

**Example Queries:**
- `302` - Murder (no changes)
- `304A` - Death by negligence (enhanced punishment)
- `124A` - Sedition (substantive changes to BNS 152)
- `497` - Adultery (repealed/decriminalized)

**Interpreting Change Types:**

- **Substantive**: Changes to legal elements/scope
- **Procedural**: Process/filing changes
- **Linguistic**: Wording changes, same meaning
- **Repealed**: Section removed from BNS
- **None**: Identical in BNS

---

### 3. Memo Generator

Generate comprehensive legal memoranda for multiple sections.

**Steps:**

1. Navigate to "Memo Generator"
2. Enter IPC sections (comma or space separated)
   - Example: `302, 304A, 420`
3. (Optional) Add query context
   - Example: "Client charged with culpable homicide"
4. Click "Generate Memorandum"

**Output:**

A professional legal memorandum including:

- Executive Summary
- Section-by-section analysis
- IPC vs BNS comparison
- Doctrinal changes
- Landmark cases with ratios
- **Validity Warnings** (Critical, High, Medium)
- Recommendations

**Actions:**
- **Copy**: Copy memo to clipboard
- **Download**: Save as .txt file

**Use Cases:**

- **Pre-litigation research**: Understand applicable sections
- **Client briefings**: Explain law changes
- **Court filings**: Reference valid precedents
- **Legal education**: Study IPC→BNS transitions

---

### 4. Case Search

Semantic search over landmark cases using RAG technology.

**Steps:**

1. Navigate to "Case Search"
2. Enter a natural language query
3. Click "Search Cases"

**Example Queries:**

- "What is grave and sudden provocation in murder cases?"
- "Cases on sedition and freedom of speech"
- "Dishonest intention requirement for theft"
- "Difference between murder and culpable homicide"
- "Dowry death burden of proof"

**Search Features:**

- **Semantic Understanding**: Finds conceptually relevant cases
- **Relevance Scoring**: Percentage match to query
- **Validity Status**: Shows current applicability
- **Case Metadata**: Citation, court, year
- **Excerpts**: Relevant portions highlighted

**Understanding Results:**

- **Relevance %**: Higher = better match
- **Validity Badge**:
  - Green (Valid): Fully applicable
  - Yellow (Review): Requires verification under BNS
  - Orange (Questionable): Uncertain applicability
  - Red (Invalid): Not applicable

---

## API Usage

### Authentication

Currently no authentication required. In production, implement JWT tokens.

### Base URL

```
http://localhost:8000
```

### Common Endpoints

#### Get All Sections

```bash
curl http://localhost:8000/sections
```

**Filter by category:**
```bash
curl "http://localhost:8000/sections?category=Offences+Affecting+Life"
```

**Filter by changes:**
```bash
curl "http://localhost:8000/sections?has_changes=true"
```

#### Analyze Section

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ipc_section": "302"}'
```

#### Generate Memo

```bash
curl -X POST http://localhost:8000/memo \
  -H "Content-Type: application/json" \
  -d '{
    "ipc_sections": ["302", "304A"],
    "query_context": "Vehicular homicide case"
  }' > memo.json
```

**Extract memo text:**
```bash
cat memo.json | jq -r '.memo'
```

#### Search Cases

```bash
curl -X POST http://localhost:8000/cases/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "murder provocation",
    "n_results": 5
  }'
```

#### Get Statistics

```bash
curl http://localhost:8000/stats | jq
```

### Response Format

All responses are JSON:

```json
{
  "ipc_section": "302",
  "ipc_description": "Punishment for murder",
  "bns_section": "103",
  "has_changes": false,
  "validity_warnings": [],
  "landmark_cases": [...]
}
```

---

## Common Workflows

### Workflow 1: Case Preparation

**Scenario**: Client charged under IPC Section 304A (causing death by negligence)

1. **Analyze Section**:
   - Go to Section Analyzer
   - Enter `304A`
   - Note: BNS Section 106, punishment increased to 5 years

2. **Search Precedents**:
   - Go to Case Search
   - Query: "death by negligence rash driving"
   - Review Appa Balu Ingale case

3. **Generate Memo**:
   - Go to Memo Generator
   - Enter `304A`
   - Context: "Client charged with death by rash driving"
   - Download memo for client briefing

4. **Review Warnings**:
   - Check validity warnings
   - Note enhanced punishment under BNS
   - Update sentencing arguments

---

### Workflow 2: Legal Research

**Scenario**: Research sedition law changes

1. **Section Analyzer**: `124A`
   - Observe substantial changes to BNS 152
   - Note new elements: "purposely or knowingly"
   - Electronic communication included

2. **Case Search**: "Kedar Nath Singh sedition"
   - Review foundational precedent
   - Check "requires_review" status
   - Note reasoning for review

3. **Generate Comparative Memo**:
   - Sections: `124A, 121, 120B` (related offences)
   - Comprehensive analysis of state offences

---

### Workflow 3: Validity Check

**Scenario**: Verify if old case law still applies

1. **Case Search**: Search by case name or legal issue
2. **Check Validity Status**:
   - Valid: Safe to cite
   - Requires Review: Verify elements match BNS
   - Questionable: Use with caution
   - Invalid: Do not cite (e.g., adultery cases)

3. **Review Reasoning**: Read validity_reasoning field

---

## Tips & Best Practices

### For Legal Practitioners

1. **Always Cross-Reference**: Use this as starting point, not final authority
2. **Check Dates**: BNS came into effect in 2023 - verify case law date
3. **Multiple Sections**: Analyze all potentially applicable sections
4. **Update Citations**: Reference BNS sections in new filings
5. **Monitor Warnings**: Pay special attention to "critical" and "high" warnings

### For Researchers

1. **Semantic Search**: Use natural language queries for case search
2. **Category Filters**: Use API filters for targeted research
3. **Batch Analysis**: Generate memos for section groups
4. **Export Data**: Use API to export for further analysis

### For Legal Tech Developers

1. **API-First**: Build on the REST API
2. **Pagination**: Implement for large result sets (future feature)
3. **Caching**: Cache common queries to reduce load
4. **Error Handling**: Always handle 404s for missing sections

---

## Troubleshooting

### Common Issues

#### "Section not found"

**Problem**: IPC section doesn't exist in database

**Solution**:
- Check section number spelling
- Database currently covers 20+ major sections
- Contribute additional sections via GitHub

#### "No cases found"

**Problem**: Search returns empty results

**Solution**:
- Broaden search terms
- Use legal concepts not case names
- Try alternative phrasing

#### Backend connection error

**Problem**: Frontend can't reach backend

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# Restart backend
docker-compose restart backend

# Check logs
docker-compose logs backend
```

#### Database initialization fails

**Problem**: ChromaDB or SQLite errors

**Solution**:
```bash
# Remove old databases
rm -rf backend/data backend/chroma_db

# Restart with fresh DB
docker-compose down -v
docker-compose up --build
```

#### Out of memory

**Problem**: RAG system consuming too much RAM

**Solution**:
- Reduce `n_results` in case searches
- Use lighter embedding model
- Increase Docker memory limits

---

## Advanced Usage

### Custom Section Addition

Edit `backend/app/ipc_bns_data.py`:

```python
IPC_BNS_MAPPINGS.append({
    "ipc_section": "511",
    "ipc_description": "Attempting to commit offences",
    "ipc_text": "Full legal text...",
    "bns_section": "62",
    "bns_description": "Attempting to commit offences",
    "bns_text": "Full BNS text...",
    "has_changes": False,
    "change_type": "none",
    "change_summary": "No changes",
    "category": "General Provisions",
    "punishment": "Half of maximum punishment for offence"
})
```

Re-initialize database:
```bash
cd backend/app
python init_db.py
```

### Custom Case Addition

Add to `LANDMARK_CASES` in same file:

```python
{
    "case_name": "Your Case Name",
    "citation": "AIR 2020 SC 123",
    "court": "Supreme Court of India",
    "year": 2020,
    "judges": ["Judge 1", "Judge 2"],
    "ipc_sections": ["302"],
    "facts": "...",
    "legal_issues": "...",
    "judgment_summary": "...",
    "ratio_decidendi": "...",
    "validity_status": "valid",
    "validity_reasoning": "..."
}
```

---

## Performance Optimization

### For Large Deployments

1. **Use PostgreSQL**:
   ```python
   # In database.py
   DATABASE_URL = "postgresql://user:pass@localhost/legaldb"
   ```

2. **Redis Caching**:
   - Cache frequent queries
   - Cache memo generations

3. **Load Balancing**:
   - Deploy multiple backend containers
   - Use nginx reverse proxy

4. **Vector Store Optimization**:
   - Use persistent ChromaDB
   - Consider Pinecone for production scale

---

## Security Considerations

1. **API Keys**: Never commit .env files with real API keys
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Implement for public APIs
4. **Input Validation**: All user inputs are validated
5. **SQL Injection**: Using SQLAlchemy ORM prevents this

---

## Getting Help

- **Documentation**: This guide + README.md
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: Report bugs/request features
- **Code Comments**: Inline documentation in source

---

## Keyboard Shortcuts (Web UI)

- `Ctrl/Cmd + Enter`: Submit forms
- `Ctrl/Cmd + K`: Focus search input
- `Esc`: Close modals/clear search

---

**Happy Legal Research! ⚖️**
