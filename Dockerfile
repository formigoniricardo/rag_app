FROM ubuntu:24.04
FROM python:3.12

WORKDIR /ragapp

COPY . /ragapp/
# COPY requirements.txt /app/rag/

RUN python3 -m pip install -r requirements.txt

EXPOSE 8501

CMD [ "streamlit", "run", "/ragapp/usando API do google/interface_main.py" ]