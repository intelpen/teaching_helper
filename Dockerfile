# temp stage
FROM python:3.10-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

#daca vrei sa pui gcloud 
#RUN apt-get update
#RUN apt-get install apt-transport-https ca-certificates gnupg curl
#RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-cli -y   
#asta trebuie ca sa puna torch cpu
RUN pip install --no-cache-dir torch==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install --no-deps sentence-transformers
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
