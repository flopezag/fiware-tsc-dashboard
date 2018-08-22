import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .model import Base, Entity, EnablerImp, Owner, Source, Metric, Measurement, Admin

__author__ = 'Manuel Escriche'

home = os.path.dirname(os.path.abspath(__file__))
dbfile = 'sqlite:////{}/enablers-dashboard.db?check_same_thread=False'.format(home)
engine = create_engine(dbfile)
db = sessionmaker(bind=engine)()
