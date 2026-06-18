FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python create_db.py
CMD ["python", "vulnerable_app.py"]