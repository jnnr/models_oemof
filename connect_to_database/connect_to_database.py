import sqlalchemy as sa
import pandas as pd
from sqlalchemy.orm import sessionmaker
import yaml

def connect_to_db(user, passwd, host, port, DB):
    r"""
    Create connection to database.
    """
    DB_STRING = 'postgresql+psycopg2://{}:{}@{}:{}/{}'
    DB_STRING = DB_STRING.format(user, passwd, host, port, DB)

    engine = sa.create_engine(DB_STRING)
    metadata = sa.MetaData(bind=engine, reflect=True)
    engine = engine.connect()

    return engine, metadata

def upload_to_db(df, Table, engine, metadata):
    table_name = Table.name
    schema_name = Table.schema

    if not engine.dialect.has_table(engine, table_name, schema_name):
        Table.create()
        print('Created table')
    else:
        print('Table already exists')

    Session = sessionmaker(bind=engine)
    session = Session()
    # insert data
    try:
        dtype = {key: Table.columns[key].type for key in Table.columns.keys()}
        df.to_sql(table_name, engine,
                          schema='sandbox',
                          if_exists='replace',
                          dtype=dtype)
        print('Inserted to ' + table_name)
    except Exception as e:
        session.rollback()
        session.close()
        raise
        print('Insert incomplete!')
    finally:
        session.close()

    return Table


def get_df(engine, table):
    Session = sessionmaker(bind=engine)
    session = Session()
    df = pd.DataFrame(session.query(table).all())
    session.close()

    return df

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

user = cfg['user']
passwd = cfg['passwd']
host = cfg['host']
port = cfg['port']
DB = cfg['DB']

engine, metadata = connect_to_db(user, passwd, host, port, DB)

ExampleTable = sa.Table(
    'example_table_2',
    metadata,
    sa.Column('index', sa.Integer, 
              primary_key=True,
              autoincrement=True,
              nullable=False),
    sa.Column('variable', sa.VARCHAR(50)),
    sa.Column('unit', sa.VARCHAR(50)),
    sa.Column('year', sa.INTEGER),
    sa.Column('value', sa.FLOAT(50))
)

example_df = pd.read_csv('TemplateData.csv', encoding='utf8', sep=';')

ExampleTable = upload_to_db(example_df, ExampleTable, engine, metadata)


