FROM python:3.8
WORKDIR /code
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python3", "-u", "main.py"]