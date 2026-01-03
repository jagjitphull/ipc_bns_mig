# IPC/BNS Legal Reasoning Agent

## Statute Migrator with RAG + Reasoning + Memo Generation

A comprehensive AI-powered legal analysis system for analyzing the transition from the **Indian Penal Code (IPC, 1860)** to the **Bhartiya Nyaya Sanhita (BNS, 2023)**.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.109-green.svg)

---

## Features

### 1. **Structured IPC↔BNS Mapping Database**
- Complete coverage of major IPC sections (120A-500+)
- Detailed BNS equivalents with section mappings
- Doctrinal change analysis (substantive, procedural, linguistic, repealed)
- Category-wise organization
- Punishment details

### 2. **RAG-Powered Case Law Search**
- Semantic search over 12+ landmark Supreme Court cases
- Vector embeddings using Sentence Transformers
- ChromaDB for efficient retrieval
- Relevance scoring and ranking

### 3. **BNS Text Analysis & Change Detection**
- Complete BNS text corpus
- Automated doctrinal change flagging
- Severity classification (critical, high, medium)
- Legal implication analysis

### 4. **AI Legal Reasoning Agent**
- Analyzes IPC→BNS transitions
- Identifies precedent validity issues
- Generates comprehensive legal analysis
- Provides actionable recommendations

### 5. **Lawyer-Style Memo Generation**
- Professional memorandum format
- Executive summaries
- Detailed section-by-section analysis
- Validity warnings for precedents
- Recommendations for legal practitioners

### 6. **Professional Web UI**
- Interactive dashboard with statistics
- Section analyzer with change detection
- Memo generator with download/copy features
- Case law semantic search
- Responsive design

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web UI (React)                       │
│  Dashboard | Section Analyzer | Memo Generator | Case Search│
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────┴────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  ┌──────────────┐  ┌────────────┐  ┌────────────────────┐  │
│  │  Legal Agent │  │ RAG System │  │   Database (SQL)   │  │
│  │  Reasoning   │  │  ChromaDB  │  │  IPC-BNS Mappings  │  │
│  │  Memo Gen    │  │  Embeddings│  │  Landmark Cases    │  │
│  └──────────────┘  └────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Tech Stack:**
- **Backend**: Python, FastAPI, SQLAlchemy
- **Vector DB**: ChromaDB with Sentence Transformers
- **Frontend**: React, React Router, Axios
- **Database**: SQLite (easily swappable to PostgreSQL)
- **Containerization**: Docker, Docker Compose

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- **OR** Python 3.11+ and Node.js 18+

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ipc_bns_mig

# Build and start containers
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend Setup:**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
cd app
python init_db.py

# Start server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup:**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Access at http://localhost:3000
```

---

## Database Schema

### IPC-BNS Mapping Table

| Field | Type | Description |
|-------|------|-------------|
| ipc_section | String | IPC section number (e.g., "302") |
| ipc_description | Text | Section description |
| ipc_text | Text | Full legal text |
| bns_section | String | Corresponding BNS section |
| bns_text | Text | BNS legal text |
| has_changes | Boolean | Whether changes exist |
| change_type | String | substantive/procedural/linguistic/repealed/none |
| change_summary | Text | Summary of changes |
| category | String | Legal category |
| punishment | Text | Punishment details |

### Landmark Cases Table

| Field | Type | Description |
|-------|------|-------------|
| case_name | String | Full case name |
| citation | String | Legal citation |
| court | String | Court name |
| year | Integer | Year of judgment |
| facts | Text | Case facts |
| legal_issues | Text | Issues raised |
| judgment_summary | Text | Judgment summary |
| ratio_decidendi | Text | Binding legal principle |
| validity_status | String | valid/requires_review/questionable/invalid |
| validity_reasoning | Text | Why status assigned |

---

## API Endpoints

### Sections

- `GET /sections` - List all IPC sections
- `GET /section/{ipc_section}` - Get specific section details
- `POST /analyze` - Analyze IPC→BNS transition

### Memos

- `POST /memo` - Generate legal memorandum

### Cases

- `GET /cases` - List landmark cases
- `GET /cases/{case_id}` - Get case details
- `POST /cases/search` - Semantic search

### Statistics

- `GET /stats` - Database statistics
- `GET /categories` - Legal categories

**Full API Documentation:** http://localhost:8000/docs (when running)

---

## Usage Examples

### 1. Analyze a Section

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ipc_section": "302"}'
```

### 2. Generate Memo

```bash
curl -X POST http://localhost:8000/memo \
  -H "Content-Type: application/json" \
  -d '{
    "ipc_sections": ["302", "304A", "420"],
    "query_context": "Client charged with murder"
  }'
```

### 3. Search Cases

```bash
curl -X POST http://localhost:8000/cases/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "grave and sudden provocation murder",
    "n_results": 5
  }'
```

---

## Key Legal Sections Covered

### Offences Against the State
- **IPC 121** → **BNS 147**: Waging war
- **IPC 124A** → **BNS 152**: Sedition (Substantive changes)

### Offences Affecting Life
- **IPC 299-300** → **BNS 100-101**: Culpable homicide & Murder
- **IPC 302** → **BNS 103**: Punishment for murder
- **IPC 304A** → **BNS 106**: Death by negligence (Enhanced punishment)
- **IPC 304B** → **BNS 80**: Dowry death

### Sexual Offences
- **IPC 354** → **BNS 74**: Outraging modesty
- **IPC 375-376** → **BNS 63-64**: Rape
- **IPC 497** → **REPEALED**: Adultery (Decriminalized)

### Property Offences
- **IPC 378-379** → **BNS 303**: Theft
- **IPC 392** → **BNS 309**: Robbery
- **IPC 420** → **BNS 318**: Cheating

### Other Offences
- **IPC 499-500** → **BNS 356**: Defamation
- **IPC 503** → **BNS 351**: Criminal intimidation

---

## Landmark Cases Included

1. **Kedar Nath Singh v. State of Bihar (1962)** - Sedition
2. **K.M. Nanavati v. State of Maharashtra (1962)** - Murder & Provocation
3. **State of Karnataka v. Appa Balu Ingale (1993)** - Death by Negligence
4. **Sushil Murmu v. State of Jharkhand (2004)** - Dowry Death
5. **Mukesh v. State of NCT Delhi (2017)** - Nirbhaya Case (Rape)
6. **Joseph Shine v. Union of India (2018)** - Adultery Decriminalized
7. **Subramanian Swamy v. Union of India (2016)** - Criminal Defamation
8. **Shreya Singhal v. Union of India (2015)** - Free Speech Online

And more...

---

## Validity Warning System

The system automatically flags precedents with:

### Critical Warnings
- Section repealed/decriminalized
- Fundamental legal framework changed

### High Priority Warnings
- Substantive changes in elements of offence
- Punishment modifications
- Doctrinal shifts

### Advisory Warnings
- Cases requiring review under new framework
- Questionable continued applicability
- Changed legal context

---

## Development

### Project Structure

```
ipc_bns_mig/
├── backend/
│   ├── app/
│   │   ├── database.py          # DB models
│   │   ├── ipc_bns_data.py      # Mappings & cases
│   │   ├── rag_system.py        # Vector search
│   │   ├── legal_agent.py       # Reasoning engine
│   │   ├── main.py              # FastAPI app
│   │   └── init_db.py           # DB initialization
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── Dashboard.js
│   │   │   ├── SectionAnalyzer.js
│   │   │   ├── MemoGenerator.js
│   │   │   └── CaseSearch.js
│   │   ├── services/
│   │   │   └── api.js
│   │   └── styles/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

### Adding More Sections

Edit `backend/app/ipc_bns_data.py`:

```python
IPC_BNS_MAPPINGS.append({
    "ipc_section": "XYZ",
    "ipc_description": "...",
    "ipc_text": "...",
    "bns_section": "ABC",
    # ... other fields
})
```

### Adding More Cases

```python
LANDMARK_CASES.append({
    "case_name": "...",
    "citation": "...",
    "ipc_sections": ["XYZ"],
    # ... other fields
})
```

---

## Deployment

### Production Deployment

1. **Update environment variables** in `.env`:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Use PostgreSQL** (optional):
   ```python
   # In database.py
   DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
   ```

3. **Enable CORS** properly:
   ```python
   # In main.py
   allow_origins=["https://yourdomain.com"]
   ```

4. **Deploy with docker-compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

---

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## Limitations & Disclaimers

⚠️ **Important Legal Disclaimer:**

1. This is an **automated analysis tool** - not a substitute for legal advice
2. All outputs should be **reviewed by qualified legal professionals**
3. The system provides **guidance**, not definitive legal opinions
4. Case law and statutory interpretations evolve - always verify currency
5. Not all IPC sections are covered - this is a representative sample
6. Validity warnings are **advisory** - independent legal research required

---

## Future Enhancements

- [ ] Complete coverage of all 511 IPC sections
- [ ] Integration with live case law databases
- [ ] Advanced LLM integration (Claude, GPT-4) for deeper reasoning
- [ ] Multi-language support (Hindi, regional languages)
- [ ] PDF report generation
- [ ] User authentication and saved analyses
- [ ] Comparison with CrPC→BNSS and Evidence Act→BSE transitions
- [ ] Real-time updates as BNS case law develops

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

## Acknowledgments

- Indian Penal Code, 1860
- Bhartiya Nyaya Sanhita, 2023
- Supreme Court of India case law
- Open source legal tech community

---

## Contact & Support

For issues, questions, or contributions:
- GitHub Issues: [Report bugs or request features]
- Documentation: See `/docs` folder

---

## Version History

**v1.0.0** (2026-01-03)
- Initial release
- 20+ IPC sections covered
- 12+ landmark cases
- Full RAG system
- Web UI with 4 modules
- Docker containerization

---

**Built with ⚖️ for the legal community**
