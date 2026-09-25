# --- Stage 1: Build & Dependencies Layer ---
FROM python:3.10-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Runtime Production Layer ---
FROM python:3.10-slim
WORKDIR /app

# Copy installed python dependencies from builder stage
COPY --from=builder /root/.local /root/.local
COPY . /app

# Ensure dependencies in root local bin are accessible
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Create a non-root system user for strict container security compliance
RUN useradd -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

# Default execution target running system audit utility
ENTRYPOINT ["python", "sys_audit.py"]