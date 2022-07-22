from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UrlsTable(Base):
    __tablename__ = 'Urls'

    id = Column(String, primary_key=True)
    url = Column(String)
    create_date = Column(DateTime, server_default=func.now())


Index('id_hash', UrlsTable.id, postgresql_using='hash')
