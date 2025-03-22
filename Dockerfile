FROM python:3.12
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV DATABASE_HOST=host.docker.internal
ENTRYPOINT ["python", "m_main.py"]

