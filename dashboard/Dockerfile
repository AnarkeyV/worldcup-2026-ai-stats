FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:${PATH}"

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r /app/requirements.txt && \
    python -m pip show streamlit

COPY app.py /app/app.py

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "/app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]