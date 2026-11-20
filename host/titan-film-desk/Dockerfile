FROM python:3.12-slim-bookworm
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --uid 10001 --create-home --shell /usr/sbin/nologin titan
WORKDIR /app
COPY titan_film.py ./titan_film.py
COPY web ./web
RUN mkdir -p /data && chown titan:titan /data
USER titan
ENV TITAN_MEDIA_ROOT=/data PYTHONDONTWRITEBYTECODE=1
EXPOSE 8786
CMD ["python3","titan_film.py","--root","/data","serve","--bind","0.0.0.0","--port","8786"]
