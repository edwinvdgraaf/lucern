import datetime
import json

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.types import TIMESTAMP, TypeDecorator, VARCHAR

from settings import DB_URL

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

metadata = MetaData()

# TODO add NOT NULLs
# TODO add uniques

capturesessions = Table('capturesession', metadata,
 Column('id', Integer, primary_key=True),
 Column('name', String),
 Column('created', DateTime, default=datetime.datetime.utcnow),
 Column('resolutionX', Integer),
) # TODO change how resolution field works

screenshots = Table('screenshot', metadata,
 Column('id', Integer, primary_key=True),
 Column('uuid', String),
 Column('url', String),
 Column('capturesession_id', Integer),
 Column('resolutionX', Integer),
 Column('browser', JSONEncodedDict),
)

engine = create_engine(DB_URL)
