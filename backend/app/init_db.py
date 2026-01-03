"""
Database initialization script
Populates the database with IPC-BNS mappings and landmark cases
"""
import sys
from sqlalchemy.orm import Session

from database import init_db, IPCBNSMapping, LandmarkCase
from ipc_bns_data import IPC_BNS_MAPPINGS, LANDMARK_CASES
from rag_system import CaseLawRAG


def populate_database():
    """Populate database with IPC-BNS mappings and landmark cases"""

    print("Initializing database...")
    engine, SessionLocal = init_db()
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_sections = db.query(IPCBNSMapping).count()
        if existing_sections > 0:
            print(f"Database already contains {existing_sections} sections.")
            response = input("Do you want to clear and repopulate? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return

            # Clear existing data
            db.query(IPCBNSMapping).delete()
            db.query(LandmarkCase).delete()
            db.commit()
            print("Cleared existing data.")

        # Add IPC-BNS mappings
        print(f"\nAdding {len(IPC_BNS_MAPPINGS)} IPC-BNS section mappings...")
        section_map = {}

        for mapping_data in IPC_BNS_MAPPINGS:
            mapping = IPCBNSMapping(
                ipc_section=mapping_data['ipc_section'],
                ipc_description=mapping_data['ipc_description'],
                ipc_text=mapping_data['ipc_text'],
                bns_section=mapping_data.get('bns_section'),
                bns_description=mapping_data.get('bns_description'),
                bns_text=mapping_data.get('bns_text'),
                has_changes=mapping_data.get('has_changes', False),
                change_type=mapping_data.get('change_type'),
                change_summary=mapping_data.get('change_summary'),
                category=mapping_data.get('category'),
                punishment=mapping_data.get('punishment')
            )
            db.add(mapping)
            section_map[mapping_data['ipc_section']] = mapping

        db.commit()
        print(f"✓ Added {len(IPC_BNS_MAPPINGS)} section mappings")

        # Add landmark cases
        print(f"\nAdding {len(LANDMARK_CASES)} landmark cases...")
        cases_added = []

        for case_data in LANDMARK_CASES:
            case = LandmarkCase(
                case_name=case_data['case_name'],
                citation=case_data['citation'],
                court=case_data['court'],
                year=case_data['year'],
                judges=str(case_data.get('judges', [])),
                facts=case_data['facts'],
                legal_issues=case_data['legal_issues'],
                judgment_summary=case_data['judgment_summary'],
                ratio_decidendi=case_data['ratio_decidendi'],
                obiter_dicta=case_data.get('obiter_dicta'),
                validity_status=case_data.get('validity_status', 'valid'),
                validity_reasoning=case_data.get('validity_reasoning')
            )

            # Link to IPC sections
            for ipc_section in case_data.get('ipc_sections', []):
                if ipc_section in section_map:
                    case.sections.append(section_map[ipc_section])

            db.add(case)
            cases_added.append(case)

        db.commit()
        print(f"✓ Added {len(LANDMARK_CASES)} landmark cases")

        # Initialize RAG system
        print("\nInitializing RAG system with case law...")
        rag = CaseLawRAG()

        # Prepare case data for RAG
        rag_cases = []
        for case_data in LANDMARK_CASES:
            rag_cases.append(case_data)

        rag.add_cases(rag_cases)
        print("✓ RAG system initialized with vector embeddings")

        # Print statistics
        print("\n" + "=" * 60)
        print("DATABASE INITIALIZATION COMPLETE")
        print("=" * 60)
        print(f"Total IPC Sections: {db.query(IPCBNSMapping).count()}")
        print(f"Sections with Changes: {db.query(IPCBNSMapping).filter(IPCBNSMapping.has_changes == True).count()}")
        print(f"Repealed Sections: {db.query(IPCBNSMapping).filter(IPCBNSMapping.change_type == 'repealed').count()}")
        print(f"Total Landmark Cases: {db.query(LandmarkCase).count()}")
        print("=" * 60)

        print("\n✓ Database ready for use!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_database()
