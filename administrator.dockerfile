FROM python:3

RUN mkdir -p /opt/src/administrator
WORKDIR /opt/src/administrator

COPY administrator/application.py ./application.py
COPY administrator/configuration.py ./configuration.py
COPY administrator/models.py ./models.py
COPY administrator/roleCheckDecorator.py ./roleCheckDecorator.py
COPY administrator/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]