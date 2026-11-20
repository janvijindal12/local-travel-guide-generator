FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY data ./data
COPY .env.example ./.env.example
EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.address=0.0.0.0"]
