FROM python:3.6.9

COPY /src/ /bot

RUN pip install requests websockets python-interface aiohttp

ENTRYPOINT ["/bot/main.py"]
