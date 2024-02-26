FROM python:3.11

WORKDIR /usr/src/chatbot

COPY ./requirements.txt /usr/src/chatbot/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /usr/src/chatbot/requirements.txt
COPY chroma_utils.py /usr/src/chatbot/chroma_utils.py
COPY app.py /usr/src/chatbot/app.py
COPY load_files.py /usr/src/chatbot/load_files.py
COPY data/*  /usr/src/chatbot/data/
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "7860", "app:app"]