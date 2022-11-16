FROM python:3.10.2

#COPY /src/ /bot

VOLUME ["/bot"]

RUN pip install requests websockets python-interface aiohttp mysql-connector

RUN groupadd -r botuser -g 1000 && \
    useradd -u 1000 -r -g botuser -s /sbin/nologin -c "Docker image user" botuser

USER botuser

CMD ["python","-u","/bot/main.py"]
#ENTRYPOINT ["/bot/main.py"]
