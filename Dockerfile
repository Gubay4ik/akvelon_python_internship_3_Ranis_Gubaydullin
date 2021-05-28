FROM python:3.10.0b1-alpine3.13

WORKDIR /code

COPY src/* src/

COPY requirements.txt ./
RUN pip install -r requirements.txt

ENV FLASK_APP src/app.py
ENV FLASK_ENV development
ENV FLASK_DEBUG 0

EXPOSE 5000

CMD ["python", "src/app.py"]


