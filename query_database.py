#!/usr/bin/env python3
"""
Interactive Database Query Tool
Quickly search and explore the expanded IPC/BNS database
"""

import sys
sys.path.insert(0, 'backend/app')

from ipc_bns_data import IPC_BNS_MAPPINGS, LANDMARK_CASES
import json

def display_section(section):
    """Display a section in a formatted way"""
    print("\n" + "=" * 80)
    print(f"IPC SECTION {section['ipc_section']}: {section['ipc_description']}")
    print("=" * 80)

    print(f"\n📖 IPC Text:")
    print(f"   {section['ipc_text'][:200]}...")

    if section.get('bns_section'):
        print(f"\n🔄 BNS Equivalent:")
        print(f"   Section {section['bns_section']}: {section['bns_description']}")
    else:
        print(f"\n⚠️  Status: {section.get('change_type', 'unknown').upper()}")

    print(f"\n📊 Category: {section['category']}")
    print(f"⚖️  Punishment: {section['punishment']}")

    print(f"\n🔍 Changes:")
    print(f"   Type: {section['change_type']}")
    print(f"   Summary: {section['change_summary']}")

def display_case(case):
    """Display a landmark case in a formatted way"""
    print("\n" + "=" * 80)
    print(f"{case['case_name']}")
    print("=" * 80)

    print(f"\n📜 Citation: {case['citation']}")
    print(f"🏛️  Court: {case['court']}")
    print(f"📅 Year: {case['year']}")
    print(f"👨‍⚖️  Judges: {', '.join(case['judges'][:3])}")
    if len(case['judges']) > 3:
        print(f"         + {len(case['judges']) - 3} more")

    print(f"\n🔗 Related IPC Sections: {', '.join(case['ipc_sections'])}")

    print(f"\n📖 Facts:")
    print(f"   {case['facts'][:300]}...")

    print(f"\n⚖️  Ratio Decidendi:")
    print(f"   {case['ratio_decidendi'][:300]}...")

    print(f"\n✅ Validity Status: {case['validity_status'].upper()}")
    print(f"   {case['validity_reasoning'][:200]}...")

def search_sections(query):
    """Search for sections by keyword"""
    query = query.lower()
    results = []

    for section in IPC_BNS_MAPPINGS:
        if (query in section['ipc_section'].lower() or
            query in section['ipc_description'].lower() or
            query in section['ipc_text'].lower() or
            query in section['category'].lower()):
            results.append(section)

    return results

def search_cases(query):
    """Search for cases by keyword"""
    query = query.lower()
    results = []

    for case in LANDMARK_CASES:
        if (query in case['case_name'].lower() or
            query in case['facts'].lower() or
            query in case['legal_issues'].lower() or
            any(query in section.lower() for section in case['ipc_sections'])):
            results.append(case)

    return results

def list_categories():
    """List all categories with counts"""
    categories = {}
    for section in IPC_BNS_MAPPINGS:
        cat = section['category']
        categories[cat] = categories.get(cat, 0) + 1

    print("\n📚 CATEGORIES:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   • {cat}: {count} sections")

def show_statistics():
    """Display database statistics"""
    print("\n" + "=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)

    print(f"\n📊 Overview:")
    print(f"   • Total IPC Sections: {len(IPC_BNS_MAPPINGS)}")
    print(f"   • Total Landmark Cases: {len(LANDMARK_CASES)}")

    list_categories()

    print(f"\n⚖️  Change Types:")
    change_types = {}
    for section in IPC_BNS_MAPPINGS:
        ct = section['change_type']
        change_types[ct] = change_types.get(ct, 0) + 1
    for ct, count in sorted(change_types.items()):
        print(f"   • {ct}: {count}")

    print(f"\n📅 Case Timeline:")
    years = [case['year'] for case in LANDMARK_CASES]
    print(f"   • Earliest: {min(years)}")
    print(f"   • Latest: {max(years)}")
    print(f"   • 21st Century: {len([y for y in years if y >= 2000])}")

    print(f"\n✅ Case Validity:")
    validity = {}
    for case in LANDMARK_CASES:
        vs = case['validity_status']
        validity[vs] = validity.get(vs, 0) + 1
    for vs, count in sorted(validity.items()):
        print(f"   • {vs}: {count}")

def show_new_additions():
    """Show sections and cases added in the expansion"""
    print("\n" + "=" * 80)
    print("NEW ADDITIONS IN DATABASE EXPANSION")
    print("=" * 80)

    new_sections = [
        "107", "109", "141", "143", "147", "295A", "306", "307",
        "320", "323", "325", "326", "363", "365", "366", "377",
        "384", "403", "405", "406", "415", "417", "425", "426",
        "463", "465", "467", "468", "471", "498A"
    ]

    print(f"\n📝 New IPC Sections ({len(new_sections)}):")
    for section_num in new_sections:
        section = next((s for s in IPC_BNS_MAPPINGS if s['ipc_section'] == section_num), None)
        if section:
            print(f"   • {section_num}: {section['ipc_description']}")

    print(f"\n📚 Key Landmark Cases Added:")
    key_cases = [
        "Navtej Singh Johar", "Bachan Singh", "Vishaka", "D.K. Basu",
        "Arnesh Kumar", "Sharad Birdhichand Sarda", "Joseph Shine",
        "Lalita Kumari", "Machhi Singh", "Mukesh"
    ]

    for key_case in key_cases:
        case = next((c for c in LANDMARK_CASES if key_case in c['case_name']), None)
        if case:
            print(f"   • {case['case_name']} ({case['year']})")

def interactive_mode():
    """Run interactive query mode"""
    print("\n" + "=" * 80)
    print("IPC/BNS DATABASE QUERY TOOL")
    print("=" * 80)
    print("\nCommands:")
    print("  section <number>    - Look up IPC section (e.g., 'section 307')")
    print("  search <keyword>    - Search sections and cases (e.g., 'search murder')")
    print("  case <name>         - Search for a case (e.g., 'case Navtej')")
    print("  categories          - List all categories")
    print("  stats               - Show database statistics")
    print("  new                 - Show new additions")
    print("  quit                - Exit")
    print("\n" + "=" * 80)

    while True:
        try:
            command = input("\n> ").strip()

            if not command:
                continue

            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            elif cmd == 'section':
                section_num = arg.strip()
                section = next((s for s in IPC_BNS_MAPPINGS if s['ipc_section'] == section_num), None)
                if section:
                    display_section(section)
                else:
                    print(f"❌ Section {section_num} not found")

            elif cmd == 'search':
                if not arg:
                    print("❌ Please provide a search term")
                    continue

                sections = search_sections(arg)
                cases = search_cases(arg)

                if sections:
                    print(f"\n📖 Found {len(sections)} matching sections:")
                    for s in sections[:5]:
                        print(f"   • IPC {s['ipc_section']}: {s['ipc_description']}")
                    if len(sections) > 5:
                        print(f"   ... and {len(sections) - 5} more")

                if cases:
                    print(f"\n⚖️  Found {len(cases)} matching cases:")
                    for c in cases[:5]:
                        print(f"   • {c['case_name']} ({c['year']})")
                    if len(cases) > 5:
                        print(f"   ... and {len(cases) - 5} more")

                if not sections and not cases:
                    print(f"❌ No results found for '{arg}'")

            elif cmd == 'case':
                if not arg:
                    print("❌ Please provide a case name")
                    continue

                cases = search_cases(arg)
                if cases:
                    display_case(cases[0])
                    if len(cases) > 1:
                        print(f"\nℹ️  Found {len(cases) - 1} more matching case(s)")
                else:
                    print(f"❌ No cases found matching '{arg}'")

            elif cmd == 'categories':
                list_categories()

            elif cmd == 'stats':
                show_statistics()

            elif cmd == 'new':
                show_new_additions()

            else:
                print(f"❌ Unknown command: {cmd}")
                print("Type 'section', 'search', 'case', 'categories', 'stats', 'new', or 'quit'")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command-line mode
        command = sys.argv[1].lower()

        if command == 'stats':
            show_statistics()
        elif command == 'new':
            show_new_additions()
        elif command == 'categories':
            list_categories()
        elif command == 'section' and len(sys.argv) > 2:
            section_num = sys.argv[2]
            section = next((s for s in IPC_BNS_MAPPINGS if s['ipc_section'] == section_num), None)
            if section:
                display_section(section)
            else:
                print(f"Section {section_num} not found")
        elif command == 'search' and len(sys.argv) > 2:
            query = ' '.join(sys.argv[2:])
            sections = search_sections(query)
            cases = search_cases(query)

            if sections:
                print(f"\nFound {len(sections)} sections:")
                for s in sections:
                    print(f"  • IPC {s['ipc_section']}: {s['ipc_description']}")

            if cases:
                print(f"\nFound {len(cases)} cases:")
                for c in cases:
                    print(f"  • {c['case_name']} ({c['year']})")
        else:
            print("Usage:")
            print("  python3 query_database.py stats")
            print("  python3 query_database.py new")
            print("  python3 query_database.py categories")
            print("  python3 query_database.py section <number>")
            print("  python3 query_database.py search <keyword>")
            print("\nOr run without arguments for interactive mode")
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
