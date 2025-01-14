FROM python:3.8

RUN useradd -m -U app

COPY rest_server/requirements.txt ./rest_server_requirements.txt
COPY web_app/requirements.txt ./web_app_requirements.txt
RUN pip install --no-cache-dir -r rest_server_requirements.txt -r web_app_requirements.txt

WORKDIR /home/app
USER app

COPY --chown=app:app . .

ENV PYTHONPATH=/home/app

CMD ["python", "-m", "rest_server"]
CMD ["python", "-m", "web_app"]