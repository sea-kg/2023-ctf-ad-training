FROM python:3

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8888
COPY ./* /app/
CMD ["python", "-u", "/app/server.py"]
