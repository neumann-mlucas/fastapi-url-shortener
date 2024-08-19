FROM python:3.12-slim AS builder
RUN useradd -rm -d /home/user -u 1001 user && \
    mkdir -p /home/user/fastapi-url-shortener && \
    chown -R user /home/user/fastapi-url-shortener
USER user

WORKDIR /home/user/

COPY poetry.lock pyproject.toml README.md fastapi-url-shortener/
COPY app/ fastapi-url-shortener/app/

WORKDIR /home/user/fastapi-url-shortener

ENV PATH="${PATH}:/home/user/.local/bin"

RUN pip install --upgrade pip && \ 
    pip install poetry==1.8.3 --user --no-cache-dir && \ 
    poetry config virtualenvs.in-project true && \
    poetry install --only main


FROM python:3.12-slim
RUN useradd -rm -d /home/user -u 1001 user && \
    mkdir -p /home/user/app && \
    chown -R user /home/user/app
USER user

COPY --from=builder /home/user/fastapi-url-shortener/ /home/user/fastapi-url-shortener/
ENV PATH=/home/user/fastapi-url-shortener/.venv/bin:$PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /home/user/fastapi-url-shortener

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
