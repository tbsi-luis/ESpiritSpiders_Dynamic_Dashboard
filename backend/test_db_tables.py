#!/usr/bin/env python3
"""
Direct database table checker using SQLAlchemy
Run with: python -m test_db_tables
or: python test_db_tables.py
"""

import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.config import get_settings
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseTableChecker:
    """Check database tables and data accessibility"""
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.test_results = []
        
    def connect(self):
        """Establish database connection"""
        print("\n🔗 Connecting to Database...")
        try:
            self.engine = create_engine(
                self.settings.DATABASE_URL,
                echo=False,
                pool_pre_ping=True
            )
            
            # Test the connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    print(f"   ✅ Connected successfully")
                    print(f"   📍 Host: {self.settings.DATABASE_HOST}:{self.settings.DATABASE_PORT}")
                    print(f"   📦 Database: {self.settings.DATABASE_NAME}")
                    return True
        except SQLAlchemyError as e:
            print(f"   ❌ Connection failed: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def get_all_tables(self):
        """Get list of all tables in database"""
        print("\n📋 Fetching All Tables...")
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"   ✅ Found {len(tables)} table(s)")
                for table in tables:
                    print(f"      • {table}")
                self.test_results.append(("Get all tables", True, f"Found {len(tables)} tables"))
                return tables
            else:
                print(f"   ⚠️  No tables found")
                self.test_results.append(("Get all tables", False, "No tables found"))
                return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append(("Get all tables", False, str(e)))
            return []
    
    def get_table_columns(self, table_name):
        """Get columns for a specific table"""
        print(f"\n📊 Table: {table_name}")
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            
            if columns:
                print(f"   ✅ Columns ({len(columns)}):")
                for col in columns:
                    col_type = col['type']
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"      • {col['name']}: {col_type} ({nullable})")
                self.test_results.append((f"Get columns for {table_name}", True, f"{len(columns)} columns"))
                return columns
            else:
                print(f"   ⚠️  No columns found")
                self.test_results.append((f"Get columns for {table_name}", False, "No columns found"))
                return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append((f"Get columns for {table_name}", False, str(e)))
            return []
    
    def get_row_count(self, table_name):
        """Get row count for a table"""
        try:
            with self.engine.connect() as conn:
                query = text(f"SELECT COUNT(*) FROM {table_name}")
                result = conn.execute(query)
                count = result.scalar()
                print(f"   📈 Row count: {count:,}")
                self.test_results.append((f"Row count for {table_name}", True, f"{count:,} rows"))
                return count
        except Exception as e:
            print(f"   ❌ Error getting row count: {e}")
            self.test_results.append((f"Row count for {table_name}", False, str(e)))
            return 0
    
    def get_sample_data(self, table_name, limit=5):
        """Get sample data from table"""
        print(f"   🔍 Sample data (first {limit} rows):")
        try:
            with self.engine.connect() as conn:
                query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
                result = conn.execute(query)
                rows = result.fetchall()
                
                if rows:
                    # Get column names
                    columns = [desc[0] for desc in result.cursor.description]
                    print(f"      Columns: {', '.join(columns[:3])}{'...' if len(columns) > 3 else ''}")
                    for i, row in enumerate(rows, 1):
                        print(f"      Row {i}: {row[:3]}{'...' if len(row) > 3 else ''}")
                    self.test_results.append((f"Sample data from {table_name}", True, f"{len(rows)} rows retrieved"))
                    return rows
                else:
                    print(f"      (no rows)")
                    self.test_results.append((f"Sample data from {table_name}", True, "0 rows (table empty)"))
                    return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append((f"Sample data from {table_name}", False, str(e)))
            return []
    
    def check_table_access(self, table_name):
        """Perform comprehensive checks on a table"""
        print(f"\n{'='*70}")
        print(f"📋 Checking Table: {table_name}")
        print(f"{'='*70}")
        
        # Get columns
        columns = self.get_table_columns(table_name)
        
        if columns:
            # Get row count
            self.get_row_count(table_name)
            
            # Get sample data
            self.get_sample_data(table_name)
            
            return True
        return False
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*70}")
        print("📊 Database Table Access Summary")
        print(f"{'='*70}")
        
        for test_name, result, details in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<50} {status}")
            if details:
                print(f"   └─ {details}")
        
        passed = sum(1 for _, r, _ in self.test_results if r)
        total = len(self.test_results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"Results: {passed}/{total} checks passed ({percentage:.1f}%)")
        print(f"{'='*70}\n")
        
        return passed, total
    
    def run(self, table_names=None):
        """Run full database check"""
        print(f"{'='*70}")
        print("🚀 Database Table Access Checker")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # Connect to database
        if not self.connect():
            print("\n❌ Cannot proceed without database connection")
            return 1
        
        # Get all tables
        all_tables = self.get_all_tables()
        
        if not all_tables:
            print("\n❌ No tables found in database")
            self.print_summary()
            return 1
        
        # Check specific tables or all tables
        tables_to_check = table_names if table_names else all_tables[:3]  # Default to first 3
        
        print(f"\n🔄 Checking {len(tables_to_check)} table(s)...\n")
        
        for table in tables_to_check:
            if table in all_tables:
                self.check_table_access(table)
            else:
                print(f"\n⚠️  Table '{table}' not found")
        
        # Print summary
        passed, total = self.print_summary()
        
        return 0 if passed == total else 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Check database tables and data accessibility'
    )
    parser.add_argument(
        'tables',
        nargs='*',
        help='Specific table names to check (leave empty to check first 3 tables)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Check all tables in database'
    )
    
    args = parser.parse_args()
    
    checker = DatabaseTableChecker()
    
    # Determine which tables to check
    if args.all:
        # Get all tables and check them
        if checker.connect():
            all_tables = checker.get_all_tables()
            exit_code = checker.run(all_tables)
        else:
            exit_code = 1
    else:
        exit_code = checker.run(args.tables if args.tables else None)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
