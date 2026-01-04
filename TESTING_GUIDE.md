# Database Expansion Testing Guide

This guide explains how to test the database expansion that added 31 new IPC sections and 38 new landmark cases.

## 📊 What Was Added

### IPC Sections (20 → 51)
- **Abetment**: 107, 109
- **Public Tranquility**: 141, 143, 147
- **Religious Offences**: 295A
- **Offences Against Life**: 306, 307
- **Hurt & Grievous Hurt**: 320, 323, 325, 326
- **Kidnapping**: 363, 365, 366
- **Decriminalized**: 377
- **Property Crimes**: 384, 403, 405, 406, 415, 417, 425, 426
- **Forgery**: 463, 465, 467, 468, 471
- **Offences Against Women**: 498A

### Landmark Cases (13 → 51)
- Constitutional Law (Navtej Singh Johar, Bachan Singh, Vishaka, Joseph Shine)
- Murder & Death Penalty (Kali Ram, Machhi Singh, Nirbhaya)
- Evidence (Sharad Birdhichand Sarda, Best Bakery, Jessica Lal)
- Criminal Procedure (D.K. Basu, Arnesh Kumar, Lalita Kumari)
- Bail (Ajay Agrawal, Arnab Goswami, Sanjay Chandra)
- And 25+ more cases across all legal domains

## 🧪 Testing Methods

### Method 1: Database Integrity Test (Recommended First)

This automated test verifies the database structure and content.

```bash
# Run the comprehensive database test
python3 test_database_expansion.py
```

**What it tests:**
- ✅ Data integrity (51 sections, 51 cases)
- ✅ All 30 new IPC sections are present
- ✅ All key landmark cases are findable
- ✅ Case details completeness (citations, judges, validity status)
- ✅ IPC→BNS mappings completeness
- ✅ Specific high-profile examples (Section 377, Nirbhaya, D.K. Basu)

**Expected output:**
```
🎉 ALL TESTS PASSED! Database expansion is complete and valid.
Passed: 6/6
Failed: 0/6
```

### Method 2: API Endpoint Testing

Tests that the backend API can serve the new data.

**Prerequisites:**
1. Backend server must be running

```bash
# Start the backend (in one terminal)
cd backend
uvicorn app.main:app --reload

# Run API tests (in another terminal)
./test_api_endpoints.sh
```

**What it tests:**
- ✅ Health check endpoint
- ✅ New IPC sections are accessible (307, 377, 295A, 498A)
- ✅ Section search works (kidnapping, forgery, abetment)
- ✅ Landmark case search (Navtej Singh Johar, D.K. Basu, Bachan Singh)
- ✅ Cases by section lookup
- ✅ All sections/cases endpoints

**Expected output:**
```
🎉 ALL API TESTS PASSED!
Passed: 15+
Failed: 0
```

### Method 3: Frontend Manual Testing

Test the user interface with the new data.

**Prerequisites:**
1. Backend and frontend servers running
2. User account created and logged in

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm start
```

**Test Cases:**

#### Test 1: Search for New Sections
1. Navigate to **Section Analyzer** page
2. Search for "Section 307"
3. ✅ Should find "Attempt to murder"
4. ✅ Should show BNS mapping (Section 109)
5. ✅ Should display enhanced punishment details

#### Test 2: Search for Decriminalized Section
1. Search for "Section 377"
2. ✅ Should show as "repealed" or "partially decriminalized"
3. ✅ Should explain consensual adult activity is legal

#### Test 3: Case Law Search
1. Navigate to **Case Search** page
2. Search for "Navtej Singh Johar"
3. ✅ Should find the 2018 Supreme Court case
4. ✅ Should show related IPC Section 377
5. ✅ Should display validity status as "valid"
6. ✅ Should show detailed facts and judgment

#### Test 4: Section-Based Case Discovery
1. Go to **Section Analyzer**
2. Look up "Section 302" (Murder)
3. Click on "Related Cases"
4. ✅ Should show Bachan Singh, Machhi Singh, etc.
5. ✅ Should show "rarest of rare" doctrine

#### Test 5: Search Multiple Keywords
1. Try searching: "custodial rights"
2. ✅ Should find D.K. Basu case
3. ✅ Should mention 11 guidelines

#### Test 6: Search by Legal Principle
1. Search: "Panchsheel"
2. ✅ Should find Sharad Birdhichand Sarda case
3. ✅ Should explain circumstantial evidence principles

### Method 4: Direct Database Queries

For developers who want to inspect the data directly.

```python
# Python interactive shell
python3

>>> import sys
>>> sys.path.insert(0, 'backend/app')
>>> from ipc_bns_data import IPC_BNS_MAPPINGS, LANDMARK_CASES

# Count sections
>>> len(IPC_BNS_MAPPINGS)
51

# Count cases
>>> len(LANDMARK_CASES)
51

# Find Section 307
>>> section_307 = next(s for s in IPC_BNS_MAPPINGS if s['ipc_section'] == '307')
>>> print(section_307['ipc_description'])
'Attempt to murder'
>>> print(section_307['bns_section'])
'109'

# Find Nirbhaya case
>>> nirbhaya = next(c for c in LANDMARK_CASES if 'Mukesh' in c['case_name'])
>>> print(nirbhaya['case_name'])
'Mukesh & Anr v. State of NCT of Delhi (Nirbhaya Case)'
>>> print(nirbhaya['year'])
2017

# Find D.K. Basu case
>>> dk_basu = next(c for c in LANDMARK_CASES if 'D.K. Basu' in c['case_name'])
>>> print(dk_basu['ratio_decidendi'][:100])
'The Court laid down 11 requirements...'

# Count cases by validity status
>>> from collections import Counter
>>> validity_counts = Counter(c['validity_status'] for c in LANDMARK_CASES)
>>> for status, count in validity_counts.items():
...     print(f"{status}: {count}")
valid: 46
requires_review: 2
superseded: 1
superseded_incorporated: 1
affirmed_expanded: 1
```

### Method 5: Docker Build Test

Verify that the database expansion works in production Docker environment.

```bash
# Build and run with Docker Compose
docker-compose up --build

# Check logs for errors
docker-compose logs backend | grep -i error
docker-compose logs frontend | grep -i error

# Test API from container
curl http://localhost:8000/api/ipc-bns/section/307

# Should return Section 307 data
```

## 🎯 Specific Test Cases

### High-Profile Sections to Test

| IPC Section | Description | BNS Section | What to Check |
|-------------|-------------|-------------|---------------|
| 307 | Attempt to murder | 109 | Enhanced punishment details |
| 377 | Unnatural offences | N/A (repealed) | Partial decriminalization note |
| 498A | Cruelty by husband | 85 | Women's protection provisions |
| 295A | Religious offences | 299 | Electronic means addition |
| 302 | Murder | 103 | Death penalty cases linked |

### Landmark Cases to Test

| Case Name | Year | Section | What to Check |
|-----------|------|---------|---------------|
| Navtej Singh Johar | 2018 | 377 | Decriminalization reasoning |
| Bachan Singh | 1980 | 302 | "Rarest of rare" doctrine |
| D.K. Basu | 1997 | - | 11 arrest guidelines |
| Arnesh Kumar | 2014 | 498A | Arrest guidelines |
| Vishaka | 1997 | 354 | Sexual harassment guidelines |
| Lalita Kumari | 2014 | - | Mandatory FIR registration |

## 📈 Expected Results

After all tests, you should see:

✅ **Database Tests**: 6/6 passed
✅ **API Tests**: 15+ endpoints responding correctly
✅ **Frontend**: All searches return relevant results
✅ **Docker Build**: No compilation errors
✅ **Data Quality**: All cases have complete citations and validity analysis

## 🐛 Troubleshooting

### Issue: "Module not found: ipc_bns_data"
**Solution:** Make sure you're in the project root directory and Python path is set correctly.

```bash
cd /home/user/ipc_bns_mig
python3 test_database_expansion.py
```

### Issue: API tests fail with "Connection refused"
**Solution:** Backend server is not running. Start it first:

```bash
cd backend
uvicorn app.main:app --reload
```

### Issue: Frontend search returns no results
**Solution:**
1. Check backend is running and accessible
2. Verify API endpoints work directly (curl test)
3. Check browser console for errors
4. Verify authentication token is valid

### Issue: Docker build fails
**Solution:**
1. Clear old containers: `docker-compose down -v`
2. Rebuild: `docker-compose up --build`
3. Check for port conflicts (8000, 3000)

## 📝 Manual Verification Checklist

- [ ] Database integrity test passes (6/6)
- [ ] API endpoints respond correctly (15+ tests)
- [ ] Section 307 searchable via frontend
- [ ] Section 377 shows decriminalization status
- [ ] Navtej Singh Johar case findable
- [ ] D.K. Basu case shows 11 guidelines
- [ ] Bachan Singh case shows "rarest of rare"
- [ ] Search for "kidnapping" finds sections 363-366
- [ ] Search for "forgery" finds sections 463-471
- [ ] All landmark cases have validity status
- [ ] Docker build succeeds
- [ ] No console errors in frontend

## 🎓 Understanding the Data

### What is "validity_status"?

Each landmark case has a validity status showing its applicability under BNS:

- **valid**: Fully applicable under BNS
- **requires_review**: May need reinterpretation for BNS
- **superseded**: Replaced by new BNS provisions
- **affirmed_expanded**: Confirmed and expanded under BNS

### What are repealed sections?

Some IPC sections (like 377 - partial, 497 - adultery) were struck down or decriminalized. These correctly have:
- `change_type: "repealed"`
- `bns_section: None`
- `bns_text: None`

This is intentional and correct.

## 📞 Support

If tests fail or you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify data file imports: `python3 -c "import backend.app.ipc_bns_data"`
3. Check API directly: `curl http://localhost:8000/api/ipc-bns/sections`
4. Review browser console for frontend errors

## 🚀 Next Steps

After successful testing:

1. ✅ All data is validated and working
2. ✅ Ready for production deployment
3. ✅ Can demonstrate to stakeholders
4. ✅ Can proceed with payment integration (Option C)
5. ✅ Can market as "50+ IPC sections, 50+ landmark cases"
