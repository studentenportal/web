# PostgreSQL 13 → 18 Production Upgrade Guide

PostgreSQL major versions use incompatible data formats. A dump/restore is required.

**Downtime:** ~5-15 minutes depending on database size.

## Prerequisites

- SSH access to production server
- Enough disk space for the SQL dump (~2x current DB size to be safe)

## Step-by-step

### 1. Put the app in maintenance / stop traffic

```bash
cd ~/deploy  # or wherever docker-compose-production.yml lives
docker compose -f docker-compose-production.yml stop studentenportal nginx
```

### 2. Dump the entire database (while PG 13 is still running)

```bash
docker compose -f docker-compose-production.yml exec postgres \
  pg_dumpall -U studentenportal > /home/studentenportal/pg13-dump-$(date +%Y%m%d).sql
```

Verify the dump is not empty:

```bash
ls -lh /home/studentenportal/pg13-dump-*.sql
head -20 /home/studentenportal/pg13-dump-*.sql
```

### 3. Stop PostgreSQL 13

```bash
docker compose -f docker-compose-production.yml stop postgres
```

### 4. Back up the old data directory (safety net)

```bash
mv /home/studentenportal/postgres-data /home/studentenportal/postgres-data-pg13-backup
```

### 5. Create a fresh data directory

```bash
mkdir -p /home/studentenportal/postgres-data
```

### 6. Pull the new image and start PG 18

Make sure `docker-compose-production.yml` has:
- `image: postgres:18`
- Volume: `/home/studentenportal/postgres-data:/var/lib/postgresql/18/docker`

(These changes are already in the committed code.)

```bash
docker compose -f docker-compose-production.yml pull postgres
docker compose -f docker-compose-production.yml up -d postgres
```

Wait for it to be ready:

```bash
docker compose -f docker-compose-production.yml logs -f postgres
# Wait until you see "database system is ready to accept connections"
```

### 7. Restore the dump

```bash
docker compose -f docker-compose-production.yml exec -T postgres \
  psql -U studentenportal -d postgres < /home/studentenportal/pg13-dump-*.sql
```

> Note: You may see some warnings about existing roles — that's normal since `pg_dumpall` includes `CREATE ROLE` statements and the `studentenportal` role already exists from the env vars.

### 8. Verify the restore

```bash
docker compose -f docker-compose-production.yml exec postgres \
  psql -U studentenportal -d studentenportal -c "\dt"
```

Check that all tables are present and have data:

```bash
docker compose -f docker-compose-production.yml exec postgres \
  psql -U studentenportal -d studentenportal -c "SELECT COUNT(*) FROM auth_user;"
```

### 9. Start the application

```bash
docker compose -f docker-compose-production.yml up -d
```

### 10. Smoke test

- Check the site loads
- Check login works
- Check a few pages with data (events, documents, etc.)

### 11. Clean up (after a few days of stable operation)

```bash
rm /home/studentenportal/pg13-dump-*.sql
rm -rf /home/studentenportal/postgres-data-pg13-backup
```

## Rollback plan

If something goes wrong after step 6:

```bash
docker compose -f docker-compose-production.yml down
rm -rf /home/studentenportal/postgres-data
mv /home/studentenportal/postgres-data-pg13-backup /home/studentenportal/postgres-data
```

Then revert `docker-compose-production.yml` to `postgres:13` with the old volume path (`/var/lib/postgresql/data`) and bring everything back up.
