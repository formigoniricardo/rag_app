# ── Oráculo Corporativo — RAG AI ──
# Imagem Alpine conforme solicitado pelo professor.
# Se o build demorar muito, troque "alpine" por "slim-bookworm" na linha abaixo.
FROM python:3.12-alpine

# Dependências de sistema para compilar psycopg2, numpy, pyarrow etc.
RUN apk add --no-cache \
    gcc g++ musl-dev postgresql-dev libpq \
    cmake make linux-headers

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "consume_api/interface_main.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.headless=true"]
