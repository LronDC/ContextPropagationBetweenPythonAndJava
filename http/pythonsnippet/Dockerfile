FROM python:3.10.10

COPY . /app/
WORKDIR /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8001
CMD ["python", "server.py"]