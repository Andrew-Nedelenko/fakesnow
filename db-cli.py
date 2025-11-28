#!/usr/bin/env python3
"""
Simple CLI script to interact with FakeSnow database
No need to know Python - just run it and follow the prompts!
"""

import snowflake.connector

def connect_to_fakesnow():
    """Connect to the local FakeSnow instance"""
    try:
        conn = snowflake.connector.connect(
            user='fake',
            password='snow',
            account='fakesnow',
            host='localhost',
            port=8080,
            protocol='http',
            session_parameters={
                'CLIENT_OUT_OF_BAND_TELEMETRY_ENABLED': False
            },
            network_timeout=5
        )
        print("✅ Connected to FakeSnow successfully!")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def run_query(conn, sql):
    """Execute a SQL query and show results"""
    try:
        cursor = conn.cursor()
        result = cursor.execute(sql)
        
        if cursor.description:
            # Query returns results
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            print(f"\n📊 Query Results ({len(rows)} rows):")
            print("─" * 60)
            
            # Print column headers
            print(" | ".join(f"{col:15}" for col in columns))
            print("─" * 60)
            
            # Print data rows
            for row in rows:
                print(" | ".join(f"{str(val):15}" for val in row))
        else:
            print("✅ Query executed successfully!")
            
        print(f"📈 Rows affected: {cursor.rowcount}")
        
    except Exception as e:
        print(f"❌ Query failed: {e}")

def main():
    print("🔥 FakeSnow Database CLI")
    print("=" * 50)
    
    # Connect to FakeSnow
    conn = connect_to_fakesnow()
    if not conn:
        return
    
    print("\n� QUICK START - Copy and paste these commands one by one:")
    print("─" * 60)
    print("1️⃣  SHOW DATABASES;")
    print("2️⃣  CREATE DATABASE my_test_db;")
    print("3️⃣  USE DATABASE my_test_db;")
    print("4️⃣  CREATE SCHEMA my_schema;")
    print("5️⃣  USE SCHEMA my_schema;")
    print("6️⃣  CREATE TABLE users (id INT, name STRING);")
    print("7️⃣  INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob');")
    print("8️⃣  SELECT * FROM users;")
    print("9️⃣  SELECT COUNT(*) FROM users;")
    print("🔟  DROP TABLE users;")
    print("\n💡 Type 'help' for more commands, 'exit' or 'quit' to exit")
    print("─" * 60)
    
    try:
        while True:
            # Get user input
            sql = input("\n📋 Enter SQL query: ").strip()
            
            if sql.lower() in ['exit', 'quit', '']:
                break
            elif sql.lower() == 'help':
                print("\n🆘 HELP - Common Commands:")
                print("─" * 40)
                print("📋 SHOW DATABASES;                     - List all databases")
                print("📋 SHOW SCHEMAS;                       - List schemas in current database")
                print("📋 SHOW TABLES;                        - List tables in current schema")
                print("📋 CREATE DATABASE name;               - Create a new database")
                print("📋 USE DATABASE name;                  - Switch to a database")
                print("📋 CREATE SCHEMA name;                 - Create a new schema")
                print("📋 USE SCHEMA name;                    - Switch to a schema")
                print("📋 SELECT CURRENT_DATABASE();          - Show current database")
                print("📋 SELECT CURRENT_SCHEMA();            - Show current schema")
                print("─" * 40)
                continue
                
            if sql.endswith(';'):
                sql = sql[:-1]  # Remove trailing semicolon
                
            run_query(conn, sql)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()
        print("🔌 Connection closed.")

if __name__ == "__main__":
    main()