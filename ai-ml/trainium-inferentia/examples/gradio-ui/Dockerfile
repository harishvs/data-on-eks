FROM python:3.11-slim as build

WORKDIR /usr/src/chatbot

COPY requirements.txt ./

RUN pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

COPY chroma_utils.py /usr/src/chatbot/chroma_utils.py
COPY gradio-app.py /usr/src/chatbot/gradio-app.py
COPY load_files.py /usr/src/chatbot/load_files.py
COPY data/*  /usr/src/chatbot/data

ENTRYPOINT ["python", "gradio-app.py"]