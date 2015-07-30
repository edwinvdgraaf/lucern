from lib.database import metadata, engine

metadata.create_all(engine)
