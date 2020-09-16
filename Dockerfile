FROM python:3.8

RUN mkdir /app
WORKDIR /app
COPY app /app
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

EXPOSE 5000
CMD ["python", "/app/main.py"]