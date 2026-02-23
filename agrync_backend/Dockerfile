FROM python:3.13.2

WORKDIR /Agrync/agrync_backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /Agrync/agrync_backend/

EXPOSE 8000

CMD ["python", "main.py"]
