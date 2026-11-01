# Multi-stage / lightweight production container for EvalLens
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501

WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and persistent directory structure
RUN groupadd -r evallens && useradd -r -g evallens -d /app -s /sbin/nologin evallens \
    && mkdir -p /app/data /app/uploads /app/.streamlit \
    && chown -R evallens:evallens /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application runtime code
COPY --chown=evallens:evallens app.py .
COPY --chown=evallens:evallens core/ ./core/
COPY --chown=evallens:evallens config/ ./config/
COPY --chown=evallens:evallens database/ ./database/
COPY --chown=evallens:evallens ui/ ./ui/
COPY --chown=evallens:evallens .streamlit/ ./.streamlit/

# Switch to non-root user
USER evallens

# Expose default Streamlit port
EXPOSE 8501

# Streamlit Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# Launch application dynamically binding to 0.0.0.0 and respecting $PORT
ENTRYPOINT ["sh", "-c", "exec streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
