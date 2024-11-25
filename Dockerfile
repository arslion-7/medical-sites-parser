FROM python:3.12

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
    --output-document root.crt && \
    chmod 0644 root.crt

ENV TZ="Asia/Ashgabat"

COPY . .

CMD [ "python", "main.py" ]