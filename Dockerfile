# Optimized Dockerfile for free tier
FROM ollama/ollama:latest

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set conservative environment variables
ENV OLLAMA_HOST=0.0.0.0:11434
ENV OLLAMA_ORIGINS=*
ENV OLLAMA_MODELS=/app/models
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_MAX_LOADED_MODELS=1
ENV OLLAMA_FLASH_ATTENTION=0

# Create optimized startup script
COPY start_optimized.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 11434

HEALTHCHECK --interval=60s --timeout=30s --start-period=300s --retries=3 \
  CMD curl -f http://localhost:11434/api/tags || exit 1

ENTRYPOINT ["/bin/bash"]

CMD ["/app/start.sh"]
