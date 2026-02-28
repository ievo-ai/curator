FROM python:3.13-slim

LABEL maintainer="denis@27tech.co"
LABEL org.opencontainers.image.source="https://github.com/ievo-ai/curator"

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy source
COPY src/ src/
COPY curator.yaml .

# Install the package
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["curator"]
CMD ["scan", "--dry-run"]
