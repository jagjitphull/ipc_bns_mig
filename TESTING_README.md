# How to Test Database Expansion

## Quick Start - 3 Easy Methods

### ✅ Method 1: Automated Database Test (Fastest)

```bash
python3 test_database_expansion.py
```

**Output:**
```
🎉 ALL TESTS PASSED! Database expansion is complete and valid.
Passed: 6/6
```

**What it verifies:**
- ✅ 51 IPC sections present
- ✅ 51 landmark cases present
- ✅ All new sections (307, 377, 498A, etc.) are findable
- ✅ Key cases (Navtej Singh Johar, D.K. Basu, Bachan Singh) are complete
- ✅ All data has required fields
- ✅ Repealed sections handled correctly

---

### 🔍 Method 2: Interactive Database Explorer

```bash
# Quick stats
python3 query_database.py stats

# Look up specific section
python3 query_database.py section 307

# Search for anything
python3 query_database.py search "kidnapping"

# Interactive mode
python3 query_database.py
> search murder
> case Navtej
> section 377
> stats
> quit
```

**Example outputs:**

```bash
$ python3 query_database.py section 307

================================================================================
IPC SECTION 307: Attempt to murder
================================================================================

📖 IPC Text:
   Whoever does any act with such intention or knowledge...

🔄 BNS Equivalent:
   Section 109: Attempt to murder

📊 Category: Offences Affecting Life
⚖️  Punishment: Up to 10 years or life if hurt caused, and fine

🔍 Changes:
   Type: substantive
   Summary: Enhanced punishment when hurt is actually caused
```

---

### 🌐 Method 3: API Testing (With Backend Running)

**Step 1:** Start the backend
```bash
cd backend
uvicorn app.main:app --reload
```

**Step 2:** Run API tests
```bash
./test_api_endpoints.sh
```

**Output:**
```
🎉 ALL API TESTS PASSED!
Passed: 15+
Failed: 0
```

**Manual API tests:**
```bash
# Test new section
curl http://localhost:8000/api/ipc-bns/section/307

# Test landmark case search
curl "http://localhost:8000/api/cases/search?query=Navtej+Singh+Johar"

# Test section search
curl "http://localhost:8000/api/ipc-bns/search?query=kidnapping"
```

---

## What Was Added?

### 📚 IPC Sections: 20 → 51 (+155%)

**New Sections:**
- **Abetment**: 107, 109
- **Public Tranquility**: 141, 143, 147 (Unlawful assembly, rioting)
- **Religious Offences**: 295A (with electronic means)
- **Life**: 306 (Abetment of suicide), 307 (Attempt to murder)
- **Hurt**: 320, 323, 325, 326
- **Kidnapping**: 363, 365, 366
- **Decriminalized**: 377 (Unnatural offences - partial)
- **Property**: 384, 403, 405, 406, 415, 417, 425, 426
- **Forgery**: 463, 465, 467, 468, 471
- **Women**: 498A (Cruelty)

### ⚖️ Landmark Cases: 13 → 51 (+292%)

**Key Cases Added:**
1. **Navtej Singh Johar v. UoI** (2018) - Section 377 decriminalization
2. **Bachan Singh v. State of Punjab** (1980) - Death penalty "rarest of rare"
3. **D.K. Basu v. State of WB** (1997) - 11 custodial rights guidelines
4. **Vishaka v. State of Rajasthan** (1997) - Sexual harassment
5. **Arnesh Kumar v. State of Bihar** (2014) - Arrest guidelines for 498A
6. **Lalita Kumari v. Govt of UP** (2014) - Mandatory FIR registration
7. **Joseph Shine v. UoI** (2018) - Adultery decriminalized
8. **Sharad Birdhichand Sarda** (1984) - Panchsheel (circumstantial evidence)
9. **Mukesh & Anr (Nirbhaya)** (2017) - Aggravated rape
10. **Machhi Singh v. State of Punjab** (1983) - Death penalty elaboration

...and 28 more cases across all legal domains.

---

## Testing Cheat Sheet

| What to Test | Command | Expected Result |
|--------------|---------|-----------------|
| Overall integrity | `python3 test_database_expansion.py` | 6/6 tests pass |
| Database stats | `python3 query_database.py stats` | Shows 51 sections, 51 cases |
| Section 307 | `python3 query_database.py section 307` | Shows "Attempt to murder" |
| Section 377 | `python3 query_database.py section 377` | Shows "repealed" status |
| Navtej case | `python3 query_database.py search Navtej` | Finds 2018 Supreme Court case |
| D.K. Basu case | `python3 query_database.py search "D.K. Basu"` | Finds custodial rights case |
| Kidnapping sections | `python3 query_database.py search kidnapping` | Finds 363, 365, 366 |
| API health | `curl http://localhost:8000/health` | Returns 200 OK |
| API section | `curl http://localhost:8000/api/ipc-bns/section/307` | Returns section data |

---

## Verification Checklist

Run these commands and check all pass:

```bash
# 1. Database test
python3 test_database_expansion.py
# ✅ Should show: ALL TESTS PASSED (6/6)

# 2. Check stats
python3 query_database.py stats
# ✅ Should show: 51 sections, 51 cases

# 3. Test new section
python3 query_database.py section 307
# ✅ Should show: Attempt to murder, BNS 109

# 4. Test decriminalized section
python3 query_database.py section 377
# ✅ Should show: repealed status

# 5. Test landmark case
python3 query_database.py search "Navtej Singh Johar"
# ✅ Should find: 2018 case on Section 377

# 6. Test categories
python3 query_database.py categories
# ✅ Should show: 14 different categories
```

If all show ✅, your database expansion is fully working!

---

## Common Test Scenarios

### Test 1: Verify Section 307 (New Addition)
```bash
python3 query_database.py section 307
```
**Should see:**
- Description: "Attempt to murder"
- BNS Section: 109
- Enhanced punishment details
- Change type: substantive

### Test 2: Verify Section 377 (Decriminalized)
```bash
python3 query_database.py section 377
```
**Should see:**
- Status: repealed
- BNS Section: None (correctly shows no mapping)
- Explanation of partial decriminalization

### Test 3: Verify D.K. Basu Case (Custodial Rights)
```bash
python3 query_database.py search "D.K. Basu"
```
**Should see:**
- 1997 Supreme Court case
- Details about 11 arrest guidelines
- Validity status: valid

### Test 4: Search by Legal Principle
```bash
python3 query_database.py search "rarest of rare"
```
**Should find:**
- Bachan Singh case
- Machhi Singh case
- Death penalty doctrine

### Test 5: Property Crimes
```bash
python3 query_database.py search "forgery"
```
**Should find sections:**
- 463 (Definition)
- 465, 467, 468, 471 (Various forgery offences)

---

## Troubleshooting

### ❌ Problem: "Module not found"
**Solution:**
```bash
cd /home/user/ipc_bns_mig
python3 test_database_expansion.py
```

### ❌ Problem: API tests fail
**Solution:**
```bash
# Start backend first
cd backend
uvicorn app.main:app --reload

# Then run tests in another terminal
./test_api_endpoints.sh
```

### ❌ Problem: No results in search
**Solution:** Check spelling and try broader terms
```bash
# Instead of "Navtej Singh Johar v. Union of India"
python3 query_database.py search Navtej

# Instead of specific section description
python3 query_database.py search murder
```

---

## Next Steps After Testing

Once all tests pass:

1. ✅ **Database is validated** - 51 sections + 51 cases working
2. ✅ **Ready for frontend testing** - Start frontend and search for new content
3. ✅ **Ready for production** - Can deploy to staging/production
4. ✅ **Marketing ready** - Can advertise "50+ IPC sections, 50+ landmark cases"
5. ✅ **Option C ready** - Can proceed with payment integration

---

## Files Created for Testing

| File | Purpose |
|------|---------|
| `test_database_expansion.py` | Automated test suite (6 tests) |
| `query_database.py` | Interactive database explorer |
| `test_api_endpoints.sh` | API integration tests |
| `TESTING_GUIDE.md` | Comprehensive testing guide |
| `TESTING_README.md` | This quick reference |

---

## Summary

**Fastest way to verify everything works:**

```bash
# 30 seconds
python3 test_database_expansion.py && \
python3 query_database.py stats && \
python3 query_database.py section 307
```

If you see:
- ✅ "ALL TESTS PASSED"
- ✅ "51 IPC sections, 51 landmark cases"
- ✅ Section 307 details displayed

**You're done! Database expansion is fully working.** 🎉

---

For detailed testing instructions, see **TESTING_GUIDE.md**
