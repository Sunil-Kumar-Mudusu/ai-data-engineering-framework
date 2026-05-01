FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY tests/ tests/
COPY examples/ examples/
COPY pyproject.toml .

RUN pip install -e .

CMD ["pytest", "-q"]
