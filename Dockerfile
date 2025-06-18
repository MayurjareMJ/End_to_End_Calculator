### ✅ File: Dockerfile
# Use slim Python image
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# To run Streamlit: change CMD to
# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]