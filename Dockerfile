FROM python:3.10.2

COPY /src/ /bot

RUN pip install requests websockets python-interface aiohttp

ENTRYPOINT ["/bot/main.py"]
