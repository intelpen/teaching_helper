# temp stage
FROM python:3.10-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt requirements.txt ./
RUN pip install -r requirements.txt

# final stage
FROM python:3.10-slim as runner

EXPOSE 8080

COPY --from=builder /opt/venv /opt/venv

ADD . /app/
WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENTRYPOINT ["python", "-m", "streamlit", "run", "frontend/main.py", "--server.port=8080", "--server.address=0.0.0.0"]
