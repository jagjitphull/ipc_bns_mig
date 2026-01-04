#!/usr/bin/env python3
"""
Test script for verifying the database expansion
Tests all 51 IPC sections and 51 landmark cases
"""

import sys
sys.path.insert(0, 'backend/app')

from ipc_bns_data import IPC_BNS_MAPPINGS, LANDMARK_CASES

def test_data_integrity():
    """Test basic data structure integrity"""
    print("=" * 80)
    print("TEST 1: DATA INTEGRITY")
    print("=" * 80)

    # Test IPC sections
    print(f"\n✓ Total IPC sections: {len(IPC_BNS_MAPPINGS)}")
    assert len(IPC_BNS_MAPPINGS) == 51, f"Expected 51 sections, got {len(IPC_BNS_MAPPINGS)}"

    # Test landmark cases
    print(f"✓ Total landmark cases: {len(LANDMARK_CASES)}")
    assert len(LANDMARK_CASES) == 51, f"Expected 51 cases, got {len(LANDMARK_CASES)}"

    print("\n✅ Data integrity test PASSED")
    return True

def test_new_ipc_sections():
    """Test newly added IPC sections"""
    print("\n" + "=" * 80)
    print("TEST 2: NEW IPC SECTIONS")
    print("=" * 80)

    # New sections that should be present
    new_sections = [
        "107", "109",  # Abetment
        "141", "143", "147",  # Public Tranquility
        "295A",  # Religious Offences
        "306", "307",  # Life Offences
        "320", "323", "325", "326",  # Hurt
        "363", "365", "366",  # Kidnapping
        "377",  # Decriminalized
        "384", "403", "405", "406", "415", "417", "425", "426",  # Property
        "463", "465", "467", "468", "471",  # Forgery
        "498A"  # Women
    ]

    all_ipc_sections = {mapping['ipc_section'] for mapping in IPC_BNS_MAPPINGS}

    missing = []
    found = []
    for section in new_sections:
        if section in all_ipc_sections:
            found.append(section)
            print(f"  ✓ IPC {section} found")
        else:
            missing.append(section)
            print(f"  ✗ IPC {section} MISSING")

    print(f"\n✓ Found {len(found)}/{len(new_sections)} new sections")

    if missing:
        print(f"✗ Missing sections: {missing}")
        return False

    print("✅ New IPC sections test PASSED")
    return True

def test_landmark_cases():
    """Test newly added landmark cases"""
    print("\n" + "=" * 80)
    print("TEST 3: LANDMARK CASES")
    print("=" * 80)

    # Test some key landmark cases
    key_cases = [
        "Navtej Singh Johar",  # Section 377
        "Bachan Singh",  # Death penalty
        "Vishaka",  # Sexual harassment
        "D.K. Basu",  # Custodial rights
        "Arnesh Kumar",  # Arrest guidelines
        "Sharad Birdhichand Sarda",  # Panchsheel
        "Joseph Shine",  # Adultery
        "Lalita Kumari"  # FIR registration
    ]

    case_names = [case['case_name'] for case in LANDMARK_CASES]

    found = []
    missing = []
    for key_case in key_cases:
        matches = [name for name in case_names if key_case in name]
        if matches:
            found.append(key_case)
            print(f"  ✓ {key_case} found: {matches[0]}")
        else:
            missing.append(key_case)
            print(f"  ✗ {key_case} MISSING")

    print(f"\n✓ Found {len(found)}/{len(key_cases)} key landmark cases")

    if missing:
        print(f"✗ Missing cases: {missing}")
        return False

    print("✅ Landmark cases test PASSED")
    return True

def test_case_details():
    """Test that cases have all required fields"""
    print("\n" + "=" * 80)
    print("TEST 4: CASE DETAILS COMPLETENESS")
    print("=" * 80)

    required_fields = [
        'case_name', 'citation', 'court', 'year', 'judges',
        'ipc_sections', 'facts', 'legal_issues', 'judgment_summary',
        'ratio_decidendi', 'obiter_dicta', 'validity_status', 'validity_reasoning'
    ]

    incomplete_cases = []

    for case in LANDMARK_CASES:
        missing_fields = [field for field in required_fields if field not in case or not case[field]]
        if missing_fields:
            incomplete_cases.append({
                'name': case.get('case_name', 'Unknown'),
                'missing': missing_fields
            })

    if incomplete_cases:
        print(f"✗ Found {len(incomplete_cases)} incomplete cases:")
        for case in incomplete_cases[:5]:  # Show first 5
            print(f"  - {case['name']}: missing {case['missing']}")
        return False

    print(f"✓ All {len(LANDMARK_CASES)} cases have complete details")
    print("✅ Case details test PASSED")
    return True

def test_section_mappings():
    """Test IPC to BNS mappings"""
    print("\n" + "=" * 80)
    print("TEST 5: IPC→BNS MAPPINGS")
    print("=" * 80)

    required_fields = [
        'ipc_section', 'ipc_description', 'ipc_text',
        'has_changes', 'change_type', 'change_summary',
        'category', 'punishment'
    ]

    # BNS fields are optional for repealed sections
    optional_bns_fields = ['bns_section', 'bns_description', 'bns_text']

    incomplete_mappings = []

    for mapping in IPC_BNS_MAPPINGS:
        missing_fields = [field for field in required_fields if field not in mapping or mapping[field] is None]

        # For non-repealed sections, BNS fields are required
        if mapping.get('change_type') != 'repealed':
            missing_bns = [field for field in optional_bns_fields if field not in mapping or mapping[field] is None]
            missing_fields.extend(missing_bns)

        if missing_fields:
            incomplete_mappings.append({
                'section': mapping.get('ipc_section', 'Unknown'),
                'missing': missing_fields,
                'change_type': mapping.get('change_type', 'unknown')
            })

    if incomplete_mappings:
        print(f"✗ Found {len(incomplete_mappings)} incomplete mappings:")
        for mapping in incomplete_mappings[:5]:
            print(f"  - IPC {mapping['section']} ({mapping['change_type']}): missing {mapping['missing']}")
        return False

    print(f"✓ All {len(IPC_BNS_MAPPINGS)} mappings are complete")

    # Count repealed sections
    repealed = [m for m in IPC_BNS_MAPPINGS if m.get('change_type') == 'repealed']
    print(f"✓ {len(repealed)} repealed sections correctly have no BNS mapping")

    print("✅ Section mappings test PASSED")
    return True

def test_specific_examples():
    """Test specific high-profile sections and cases"""
    print("\n" + "=" * 80)
    print("TEST 6: SPECIFIC EXAMPLES")
    print("=" * 80)

    # Test Section 377 (decriminalized)
    section_377 = next((m for m in IPC_BNS_MAPPINGS if m['ipc_section'] == '377'), None)
    if section_377:
        print(f"✓ IPC 377 (Unnatural offences):")
        print(f"  - BNS Section: {section_377['bns_section']}")
        print(f"  - Change Type: {section_377['change_type']}")
        print(f"  - Category: {section_377['category']}")
    else:
        print("✗ IPC 377 not found")
        return False

    # Test Nirbhaya case
    nirbhaya = next((c for c in LANDMARK_CASES if 'Mukesh' in c['case_name'] or 'Nirbhaya' in c.get('facts', '')), None)
    if nirbhaya:
        print(f"\n✓ Nirbhaya case found:")
        print(f"  - Case: {nirbhaya['case_name']}")
        print(f"  - Year: {nirbhaya['year']}")
        print(f"  - Validity: {nirbhaya['validity_status']}")
    else:
        print("✗ Nirbhaya case not found")
        return False

    # Test D.K. Basu (custodial rights)
    dk_basu = next((c for c in LANDMARK_CASES if 'D.K. Basu' in c['case_name']), None)
    if dk_basu:
        print(f"\n✓ D.K. Basu case found:")
        print(f"  - Case: {dk_basu['case_name']}")
        print(f"  - Year: {dk_basu['year']}")
        print(f"  - Court: {dk_basu['court']}")
    else:
        print("✗ D.K. Basu case not found")
        return False

    print("\n✅ Specific examples test PASSED")
    return True

def display_statistics():
    """Display detailed statistics"""
    print("\n" + "=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)

    # IPC categories
    categories = {}
    for mapping in IPC_BNS_MAPPINGS:
        cat = mapping.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1

    print("\nIPC Sections by Category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  • {cat}: {count} sections")

    # Change types
    change_types = {}
    for mapping in IPC_BNS_MAPPINGS:
        ct = mapping.get('change_type', 'unknown')
        change_types[ct] = change_types.get(ct, 0) + 1

    print("\nChange Types:")
    for ct, count in sorted(change_types.items()):
        print(f"  • {ct}: {count} sections")

    # Case years
    years = [case['year'] for case in LANDMARK_CASES]
    print(f"\nLandmark Cases Timeline:")
    print(f"  • Earliest: {min(years)}")
    print(f"  • Latest: {max(years)}")
    print(f"  • 21st century cases: {len([y for y in years if y >= 2000])}")

    # Validity status
    validity = {}
    for case in LANDMARK_CASES:
        vs = case.get('validity_status', 'unknown')
        validity[vs] = validity.get(vs, 0) + 1

    print("\nCase Validity Status:")
    for vs, count in sorted(validity.items()):
        print(f"  • {vs}: {count} cases")

    print("\n" + "=" * 80)

def main():
    """Run all tests"""
    print("\n🔍 TESTING DATABASE EXPANSION")
    print("Testing 51 IPC sections and 51 landmark cases\n")

    tests = [
        test_data_integrity,
        test_new_ipc_sections,
        test_landmark_cases,
        test_case_details,
        test_section_mappings,
        test_specific_examples
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            failed += 1

    display_statistics()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Database expansion is complete and valid.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
