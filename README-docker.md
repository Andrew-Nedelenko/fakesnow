# FakeSnow Docker Setup 🐳❄️

This document provides instructions for building and running FakeSnow as a Docker container for testing purposes.

## Overview

FakeSnow is now available as a Docker container, allowing you to run a fake Snowflake database instance that can be accessed from your local machine or other containers. This is perfect for:

- Local development and testing
- CI/CD pipelines
- Integration testing
- Learning Snowflake without real credentials

## Quick Start

### Using Docker Compose (Recommended)

1. **Start the server:**
   ```bash
   docker-compose up -d
   ```

2. **Check the logs:**
   ```bash
   docker-compose logs fakesnow
   ```

3. **Connect to FakeSnow:**
   - Host: `localhost`
   - Port: `8080`
   - User: `fake`
   - Password: `snow`
   - Account: `fakesnow`
   - Protocol: `http`

4. **Stop the server:**
   ```bash
   docker-compose down
   ```

### Using Docker Run

```bash
# Run with default settings
docker run --rm -p 8080:8080 fakesnow:latest

# Run with custom port
docker run --rm -p 9000:9000 -e FAKESNOW_PORT=9000 fakesnow:latest

# Run with persistent database storage
docker run --rm -p 8080:8080 -v $(pwd)/data:/app/databases fakesnow:latest
```

## Building the Image

If you need to build the image yourself:

```bash
# Build the Docker image
docker build -t fakesnow:latest .

# Or use docker-compose
docker-compose build
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FAKESNOW_PORT` | `8080` | Port to run the server on |
| `FAKESNOW_HOST` | `0.0.0.0` | Host interface to bind to |
| `FAKESNOW_DB_PATH` | `/app/databases` | Path for database storage |

### Docker Compose Configuration

The `docker-compose.yml` file provides:
- **Port Mapping**: Maps container port 8080 to host port 8080
- **Persistent Storage**: Mounts `./databases` for data persistence
- **Networking**: Creates isolated network for the service
- **Health Checks**: Monitors service health
- **Restart Policy**: Automatically restarts on failure

## Connecting to FakeSnow

### From Python

```python
import snowflake.connector

# Connect to the dockerized FakeSnow
conn = snowflake.connector.connect(
    user='fake',
    password='snow',
    account='fakesnow',
    host='localhost',  # or container IP if running from another container
    port=8080,
    protocol='http',
    session_parameters={
        'CLIENT_OUT_OF_BAND_TELEMETRY_ENABLED': False
    },
    network_timeout=1
)

# Test the connection
cursor = conn.cursor()
result = cursor.execute("SELECT 'Hello from Docker FakeSnow!' as message").fetchone()
print(result)
```

### From Snowflake CLI (SnowSQL)

```bash
snowsql -a fakesnow -u fake -p snow -h localhost -P 8080 --protocol http
```

### From Other Docker Containers

If connecting from another container in the same network:

```python
# Use the service name as hostname
conn = snowflake.connector.connect(
    user='fake',
    password='snow',
    account='fakesnow',
    host='fakesnow',  # service name from docker-compose
    port=8080,
    protocol='http'
)
```

## Data Persistence

### Local Storage
Mount a local directory to persist databases:
```bash
docker run -p 8080:8080 -v $(pwd)/my-data:/app/databases fakesnow:latest
```

### Named Volumes
Use Docker named volumes:
```bash
docker volume create fakesnow-data
docker run -p 8080:8080 -v fakesnow-data:/app/databases fakesnow:latest
```

## Troubleshooting

### Container Won't Start
1. Check if port 8080 is already in use:
   ```bash
   lsof -i :8080  # or netstat -an | grep 8080
   ```
2. Use a different port:
   ```bash
   docker run -p 9000:9000 -e FAKESNOW_PORT=9000 fakesnow:latest
   ```

### Connection Refused
1. Verify the container is running:
   ```bash
   docker ps
   ```
2. Check container logs:
   ```bash
   docker logs fakesnow-server
   ```
3. Test with curl:
   ```bash
   curl -X POST http://localhost:8080/session
   ```

### Performance Issues
1. Increase memory allocation for Docker
2. Use SSD storage for database mounts
3. Consider using in-memory databases for temporary testing

## Advanced Usage

### Custom Entrypoint Commands

```bash
# Start bash shell for debugging
docker run -it --entrypoint bash fakesnow:latest

# Run custom Python script
docker run -v $(pwd)/my-script.py:/app/script.py fakesnow:latest python script.py

# Run fakesnow CLI
docker run fakesnow:latest cli --help
```

### Multi-Container Setup

Example `docker-compose.yml` for app + fakesnow:

```yaml
version: '3.8'
services:
  fakesnow:
    image: fakesnow:latest
    ports:
      - "8080:8080"
    environment:
      - FAKESNOW_DB_PATH=/app/databases
    volumes:
      - ./databases:/app/databases

  myapp:
    build: ./my-app
    depends_on:
      - fakesnow
    environment:
      - SNOWFLAKE_HOST=fakesnow
      - SNOWFLAKE_PORT=8080
```

### Health Monitoring

The container includes health checks. Monitor status:

```bash
# Check health status
docker inspect fakesnow-server | grep Health

# Watch health status
watch 'docker inspect fakesnow-server | grep Health -A 10'
```

## Development

### Building for Development

```bash
# Build development image with current code changes
docker build -t fakesnow:dev .

# Run with code mounted for live updates
docker run -p 8080:8080 -v $(pwd)/fakesnow:/app/fakesnow fakesnow:dev
```

### Debugging

```bash
# Run with debug logging
docker run -p 8080:8080 -e LOG_LEVEL=DEBUG fakesnow:latest

# Access container shell
docker exec -it fakesnow-server bash

# View application logs
docker exec fakesnow-server tail -f /app/logs/fakesnow.log
```

## Security Notes

- FakeSnow accepts any username/password combination
- Use only for development and testing
- Do not expose to public networks
- Consider using Docker secrets for production-like testing

## Performance Tips

1. **Use volumes** for database persistence instead of bind mounts
2. **Allocate sufficient memory** to Docker (4GB+ recommended)
3. **Use SSD storage** for mounted database directories
4. **Disable telemetry** in Snowflake connectors when connecting
5. **Set short timeouts** since retries aren't needed

## Examples Repository

Check the `examples/` directory (if available) for:
- Sample connection scripts
- Integration test examples
- CI/CD pipeline configurations
- Multi-language client examples

---

## Troubleshooting Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Use different port: `-p 9000:9000 -e FAKESNOW_PORT=9000` |
| Permission denied | Ensure Docker has proper permissions or run with `--user $(id -u):$(id -g)` |
| Out of disk space | Clean up Docker: `docker system prune -a` |
| Slow performance | Increase Docker memory allocation |
| Connection timeout | Check firewall settings and ensure container is accessible |

Need help? Check the [main README](README.md) or open an issue in the repository.