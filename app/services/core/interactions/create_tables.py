from database.session import Base, engine

from services.user.models import *
from services.cluster.models import *
from services.deployment.models import *
from services.authorization.models import *
from services.organization.models import *


class CreateTables:
    def __init__(self):
        pass

    def execute(self):
        Base.metadata.create_all(bind=engine)
        return {"message": "Tables Created Successfully!"}


def create_tables():
    return CreateTables().execute()
