FROM python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TEHNET_SOFTWARE_DATA=/data
WORKDIR /app
COPY requirements.lock /app/requirements.lock
COPY wheels/ /wheels/
RUN python -m pip install --no-index --find-links=/wheels --require-hashes -r requirements.lock && rm -rf /wheels
COPY app/ /app/app/
COPY catalog/ /app/catalog/
COPY templates/ /app/templates/
COPY static/ /app/static/
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 CMD ["python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/software/readyz',timeout=2)"]
CMD ["python","-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--no-proxy-headers","--no-access-log"]
