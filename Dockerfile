FROM python:3.11-slim

WORKDIR /app

# Copy all application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .[dev]

EXPOSE 7860

CMD ["literary-finder", "--host", "0.0.0.0", "--port", "7860"]