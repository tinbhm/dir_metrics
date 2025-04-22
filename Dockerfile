FROM python:3.13-slim

WORKDIR /app

COPY exporter.py .
COPY config.yml .
COPY start.sh .
RUN chmod +x start.sh

RUN pip install --no-cache-dir --root-user-action=ignore prometheus_client pyyaml

EXPOSE 3060

CMD ["/app/start.sh"]