#!/usr/bin/env python3
"""
Database migration and repair script
Ensures all tables (including auth tables) exist in the database
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, '/app/app' if os.path.exists('/app/app') else './backend/app')

from sqlalchemy import inspect, text
from database import init_db, Base
from auth_models import User, Subscription, UsageLog, SavedAnalysis, APIKey, PaymentHistory

def check_database_health(db):
    """Check database health and list existing tables"""
    inspector = inspect(db.bind)
    existing_tables = inspector.get_table_names()

    print("\n" + "="*60)
    print("DATABASE HEALTH CHECK")
    print("="*60)
    print(f"\nExisting tables ({len(existing_tables)}):")
    for table in sorted(existing_tables):
        print(f"  ✓ {table}")

    # Check expected tables
    expected_tables = [t.name for t in Base.metadata.tables.values()]
    print(f"\nExpected tables ({len(expected_tables)}):")
    for table in sorted(expected_tables):
        if table in existing_tables:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ {table} (MISSING)")

    missing_tables = set(expected_tables) - set(existing_tables)
    if missing_tables:
        print(f"\n⚠️  Missing {len(missing_tables)} tables:")
        for table in sorted(missing_tables):
            print(f"  - {table}")
        return False
    else:
        print("\n✅ All expected tables exist!")
        return True

def create_missing_tables(engine):
    """Create any missing tables"""
    print("\n" + "="*60)
    print("CREATING MISSING TABLES")
    print("="*60)

    # Create all tables (only creates missing ones)
    Base.metadata.create_all(engine)
    print("✓ Tables created/updated")

def test_auth_system(db):
    """Test if authentication system is working"""
    print("\n" + "="*60)
    print("TESTING AUTH SYSTEM")
    print("="*60)

    try:
        # Test user query
        user_count = db.query(User).count()
        print(f"✓ User table accessible - {user_count} users")

        # Test subscription query
        subscription_count = db.query(Subscription).count()
        print(f"✓ Subscription table accessible - {subscription_count} subscriptions")

        return True
    except Exception as e:
        print(f"✗ Auth system test failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("IPC/BNS LEGAL REASONING AGENT - DATABASE REPAIR")
    print("="*60)

    # Initialize database
    print("\nInitializing database connection...")
    engine, SessionLocal = init_db()
    db = SessionLocal()

    try:
        # Check database health
        is_healthy = check_database_health(db)

        if not is_healthy:
            print("\n⚠️  Database needs repair!")
            response = input("\nCreate missing tables? (yes/no): ")
            if response.lower() == 'yes':
                create_missing_tables(engine)

                # Re-check health
                print("\nRe-checking database health...")
                db.close()
                db = SessionLocal()
                check_database_health(db)
            else:
                print("Skipping table creation.")
                return

        # Test auth system
        auth_ok = test_auth_system(db)

        if auth_ok:
            print("\n" + "="*60)
            print("✅ DATABASE IS HEALTHY!")
            print("="*60)
            print("\nYou can now:")
            print("  1. Register new users")
            print("  2. Login with existing users")
            print("  3. Use all authentication features")
            print()
        else:
            print("\n" + "="*60)
            print("⚠️  DATABASE NEEDS ATTENTION")
            print("="*60)
            print("\nAuth system test failed. Please check the error above.")
            print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
