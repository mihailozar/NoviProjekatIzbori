FROM python:3

RUN mkdir -p /opt/src/voting_station
WORKDIR /opt/src/voting_station

COPY voting_station/application.py ./application.py
COPY voting_station/configuration.py ./configuration.py
COPY voting_station/roleCheckDecorator.py ./roleCheckDecorator.py
COPY voting_station/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]