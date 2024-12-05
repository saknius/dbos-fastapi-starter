import logging
from database.session import SessionLocal
from database.session import Base, engine


from services.user.models import *
from services.cluster.models import *
from services.deployment.models import *
from services.authorization.models import *
from services.organization.models import *



Base.metadata.create_all(bind=engine)


def get_celery_db():
    db = SessionLocal()
    return db
