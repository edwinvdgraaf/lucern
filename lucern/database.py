import datetime
import json

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.types import TIMESTAMP, TypeDecorator, VARCHAR

# from http://docs.sqlalchemy.org/en/rel_1_0/core/custom_types.html#marshal-json-strings
class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

DB_URL = "sqlite:///database.sqlite"

metadata = MetaData()

# TODO add NOT NULLs

capturesessions = Table('capturesession', metadata,
 Column('id', Integer, primary_key=True),
 Column('name', String, nullable=False, unique=True),
 Column('created', DateTime, nullable=False, default=datetime.datetime.utcnow),
 Column('resolutionX', Integer, nullable=False),
)

screenshots = Table('screenshot', metadata,
 Column('id', Integer, primary_key=True),
 Column('uuid', String, nullable=False),
 Column('url', String, nullable=False),
 Column('capturesession_id', Integer, nullable=False),
 Column('resolutionX', Integer, nullable=False),
 Column('browser', JSONEncodedDict, nullable=False),
)

engine = create_engine(DB_URL)
