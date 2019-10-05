FROM python:3.7

RUN apt-get update

RUN apt-get install -y pandoc

RUN useradd appuser


COPY . /app

RUN chown -R appuser /app

USER appuser
WORKDIR /app

RUN python3 -m venv /app/venv
RUN /app/venv/bin/pip install /app


EXPOSE 80

CMD /app/venv/bin/waitress-serve --port="$PORT" --call interedit.app:main
