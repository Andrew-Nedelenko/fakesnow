# FakeSnow Docker Setup - Complete Summary

## ✅ What We've Created

This repository now has a complete Docker setup for running FakeSnow locally for testing purposes.

---

## 📦 Files Added

### Docker Configuration
- `Dockerfile` - Multi-stage build with Python 3.11, non-root user, health checks
- `docker-compose.yml` - Easy deployment with port mapping and persistence
- `.dockerignore` - Optimized build context
- `docker-entrypoint.sh` - Flexible startup script

### Python Scripts
- `db-cli.py` - Interactive CLI for running SQL queries
- `setup-project.py` - Creates database, schema, and tests connection
- `setup-dimchannel.py` - Creates SODW schema and dimChannel table

### SQL Files
- `setup-queries.sql` - Manual SQL commands for database setup
- `dimchannel-queries.sql` - Complete SQL examples and workarounds

### Documentation
- `README-docker.md` - Complete Docker usage guide
- `FAKESNOW-SDK-WRAPPER-SPEC.md` - TypeScript wrapper specification for Node.js apps

---

## 🚀 Quick Start Guide

### 1. Start FakeSnow Server

```bash
# Start the server (runs on http://localhost:8080)
docker-compose up -d

# Check logs
docker-compose logs -f fakesnow

# Verify it's running
docker ps | grep fakesnow
```

### 2. Setup Your Database

```bash
# Create database and schema
docker exec fakesnow-server python /app/setup-project.py

# Create dimChannel table
docker exec fakesnow-server python /app/setup-dimchannel.py
```

### 3. Test with Interactive CLI

```bash
# Run interactive SQL CLI
docker exec -it fakesnow-server python /app/db-cli.py
```

Then try these commands:
```sql
USE DATABASE SUPER_ORDINARY_DEV;
USE SCHEMA SODW;
SELECT * FROM dimChannel;
```

### 4. Connect from Your Application

Use these environment variables:
```bash
SNOWFLAKE_ACCOUNT=fakesnow
SNOWFLAKE_USERNAME=fake
SNOWFLAKE_PASSWORD=snow
SNOWFLAKE_DATABASE=SUPER_ORDINARY_DEV
SNOWFLAKE_SCHEMA=SODW
SNOWFLAKE_WAREHOUSE=COMPUTE_WH_DEV
SNOWFLAKE_ROLE=Super_Ordinary_Dev
SNOWFLAKE_HOST=localhost
SNOWFLAKE_PORT=8080
SNOWFLAKE_PROTOCOL=http
```

---

## 🗄️ Database Structure

```
SUPER_ORDINARY_DEV (Database)
└── PUBLIC (Schema) - Default schema
└── SODW (Schema) - Your data warehouse schema
    └── dimChannel (Table)
        ├── Dim_Channel_PK: INTEGER
        ├── Channel_ID: INTEGER
        ├── Name: VARCHAR
        ├── Platform: VARCHAR
        ├── Tld: VARCHAR
        ├── Locale: VARCHAR
        ├── Currency: VARCHAR
        └── Status: VARCHAR
```

---

## 🔧 Common Commands

### Container Management
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f fakesnow

# Access shell
docker exec -it fakesnow-server bash
```

### Database Operations
```bash
# Run setup scripts
docker exec fakesnow-server python /app/setup-project.py
docker exec fakesnow-server python /app/setup-dimchannel.py

# Interactive CLI
docker exec -it fakesnow-server python /app/db-cli.py

# Run custom SQL file
docker cp my-queries.sql fakesnow-server:/app/
docker exec -it fakesnow-server python /app/db-cli.py < /app/my-queries.sql
```

### Troubleshooting
```bash
# Check if server is responding
curl -X POST http://localhost:8080/session

# View server logs
docker logs fakesnow-server

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check health
docker inspect fakesnow-server | grep -A 5 Health
```

---

## ⚠️ Important Limitations

### FakeSnow vs Real Snowflake

**❌ NOT Supported:**
- `IDENTITY(1,1)` columns
- `AUTOINCREMENT`
- `CREATE SEQUENCE`
- `CREATE WAREHOUSE` (command fails but doesn't affect usage)
- `CREATE ROLE` / `GRANT` (access control not implemented)
- Complex date/time functions
- Advanced Snowflake features

**✅ Supported:**
- Standard SQL (SELECT, INSERT, UPDATE, DELETE)
- CREATE/DROP DATABASE/SCHEMA/TABLE
- JOINs, subqueries, CTEs
- Common aggregation functions
- Parameter binding
- Most data types
- Pandas integration (Python only)

### Workarounds

**For Auto-Incrementing IDs:**

```sql
-- Instead of IDENTITY, use this pattern:
INSERT INTO dimChannel 
SELECT 
    COALESCE(MAX(Dim_Channel_PK), 0) + 1,
    101, 'New Channel', 'Web', 'com', 'en-US', 'USD', 'Active'
FROM dimChannel;
```

**For Bulk Inserts with IDs:**

```sql
INSERT INTO dimChannel
SELECT 
    ROW_NUMBER() OVER (ORDER BY source_id) + 
        COALESCE((SELECT MAX(Dim_Channel_PK) FROM dimChannel), 0),
    source_id,
    source_name,
    -- ... other columns
FROM staging_table;
```

---

## 📝 Example Queries

### Basic Operations
```sql
-- Use database and schema
USE DATABASE SUPER_ORDINARY_DEV;
USE SCHEMA SODW;

-- Insert data
INSERT INTO dimChannel VALUES 
(1, 100, 'Web', 'Website', 'com', 'en-US', 'USD', 'Active');

-- Query data
SELECT * FROM dimChannel WHERE Status = 'Active';

-- Update
UPDATE dimChannel SET Status = 'Inactive' WHERE Dim_Channel_PK = 1;

-- Delete
DELETE FROM dimChannel WHERE Status = 'Inactive';
```

### Advanced Queries
```sql
-- Aggregation
SELECT Platform, COUNT(*) as count 
FROM dimChannel 
GROUP BY Platform;

-- Join example (create another table first)
SELECT 
    c.Name,
    c.Platform,
    o.order_count
FROM dimChannel c
LEFT JOIN channel_orders o ON c.Channel_ID = o.channel_id;

-- CTE example
WITH active_channels AS (
    SELECT * FROM dimChannel WHERE Status = 'Active'
)
SELECT Platform, COUNT(*) FROM active_channels GROUP BY Platform;
```

---

## 🔗 Integration with Node.js/TypeScript

For Node.js applications using `snowflake-sdk`, see `FAKESNOW-SDK-WRAPPER-SPEC.md` for:
- Building a TypeScript wrapper
- Drop-in replacement for snowflake-sdk
- Environment variable switching between real/fake Snowflake
- Full compatibility guide

---

## 📊 Monitoring & Health Checks

```bash
# Check server health
curl -X POST http://localhost:8080/session

# Expected response: 401 error (means server is working)
# {"code":"390101","message":"Authorization header not found..."}

# Check Docker health status
docker inspect fakesnow-server --format='{{.State.Health.Status}}'

# View detailed health logs
docker inspect fakesnow-server | grep -A 20 Health
```

---

## 🗂️ Data Persistence

Data is persisted in the `./databases` directory (mounted volume):

```bash
# View persisted databases
ls -la ./databases/

# Backup data
tar -czf fakesnow-backup-$(date +%Y%m%d).tar.gz ./databases/

# Restore data
tar -xzf fakesnow-backup-20250326.tar.gz

# Clear all data
docker-compose down
rm -rf ./databases/*
docker-compose up -d
```

---

## 🎯 Next Steps

1. **For Python Apps**: Use `snowflake-connector-python` with the connection details above
2. **For Node.js Apps**: Implement the wrapper from `FAKESNOW-SDK-WRAPPER-SPEC.md`
3. **For Testing**: Write tests that use FakeSnow instead of mocking
4. **For CI/CD**: Add FakeSnow container to your pipeline

---

## 📚 Additional Resources

- Main README: `README.md`
- Docker Guide: `README-docker.md`
- SQL Examples: `dimchannel-queries.sql`, `setup-queries.sql`
- Node.js Integration: `FAKESNOW-SDK-WRAPPER-SPEC.md`
- Original Project: https://github.com/tekumara/fakesnow

---

## 🐛 Known Issues & Solutions

### Issue: "405 Method Not Allowed"
- **Cause**: Using GET instead of POST
- **Solution**: This is expected! Server is working correctly

### Issue: "IDENTITY column not supported"
- **Cause**: FakeSnow doesn't support IDENTITY syntax
- **Solution**: Use regular INTEGER and generate IDs in application

### Issue: "CREATE WAREHOUSE fails"
- **Cause**: FakeSnow doesn't implement warehouse management
- **Solution**: Ignore the error, it doesn't affect functionality

### Issue: Connection from Node.js fails
- **Cause**: snowflake-sdk tries to connect via HTTPS to *.snowflakecomputing.com
- **Solution**: Use the wrapper from `FAKESNOW-SDK-WRAPPER-SPEC.md`

---

## 🎉 You're All Set!

Your FakeSnow Docker instance is ready for testing. You can now:
- ✅ Run SQL queries locally
- ✅ Test database operations without real Snowflake
- ✅ Develop and test offline
- ✅ Use in CI/CD pipelines
- ✅ Save on Snowflake costs during development

Happy testing! 🚀
