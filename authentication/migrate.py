from flask import Flask;
from configuration import Configuration;
from flask_migrate import Migrate, init, migrate, upgrade;
from models import database, Role, User;
from sqlalchemy_utils import database_exists, create_database;
import os

application = Flask(__name__);
application.config.from_object(Configuration);
migrateObject = Migrate(application, database);
done = False;

while not done:
    try:
        if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"]);

        database.init_app(application);

        with application.app_context() as context:
            init();
            migrate(message="prva migracija migration");
            upgrade();
            adminRole = Role(name="admin");

            database.session.add(adminRole);
            database.session.commit();
            admin = User( id="0000000000000", forename="admin", surname="admin", email="admin@admin.com",
                                 password="1", roleId=adminRole.id);

            database.session.add(admin);
            database.session.commit();

            officialRole = Role(name="user");

            database.session.add(officialRole);
            database.session.commit();

            user=User(id="0803999710277", forename="Mihailo", surname="Zarkovic", email="mihailozar@gmail.com",
                                 password="zarkovic", roleId=officialRole.id)
            database.session.add(user);
            database.session.commit();

            done = True;
    except Exception as error:
        print(error);
