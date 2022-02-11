FROM python:3

RUN mkdir -p /opt/src/dbelection
WORKDIR /opt/src/dbelection

COPY administrator/migrate.py ./migrate.py
COPY administrator/configuration.py ./configuration.py
COPY administrator/models.py ./models.py
COPY administrator/roleCheckDecorator.py ./roleCheckDecorator.py
COPY administrator/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]