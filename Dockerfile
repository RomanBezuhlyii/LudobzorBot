FROM python:3.9

RUN mkdir -p /usr/src/Ludobzor_bot/
WORKDIR /usr/src/Ludobzor_bot/
VOLUME /usr/src/Ludobzor_bot/database/

COPY . /usr/src/Ludobzor_bot/
RUN pip install -r requirements.txt

EXPOSE 8080
EXPOSE 5000
EXPOSE 4444

CMD ["python","bot.py"]