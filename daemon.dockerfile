FROM python:3

RUN mkdir -p /opt/src/demon
WORKDIR /opt/src/demon

COPY daemon/application.py ./application.py
COPY daemon/configuration.py ./configuration.py
COPY daemon/models.py ./models.py
COPY daemon/requirements.txt ./requirements.txt



RUN pip install -r ./requirements.txt


ENTRYPOINT ["python","./application.py"]
