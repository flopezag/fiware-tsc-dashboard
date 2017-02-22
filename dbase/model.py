from sqlalchemy import Column, ForeignKey, Integer, Float, String, Date, PickleType, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

__author__ = 'Manuel Escriche'

Base = declarative_base()


class Entity(Base):
    """Owner's entities """
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True)
    shortname = Column(String(10), unique=True, nullable=False)
    name = Column(String)
    workers = relationship("Owner", back_populates='entity')

    def __str__(self):
        return 'Entity:[{0}]:{1} => {2} has {3}'.format(self.id, self.shortname, self.name, self.workers)


class Owner(Base):
    """ Owner's enablers """
    __tablename__ = 'owners'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    shortname = Column(String)
    email = Column(String)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    entity = relationship("Entity", back_populates='workers')
    implementations = relationship('EnablerImp', back_populates='owner')

    def __str__(self):
        return 'Owner:[{0.id}]:{0.name} in {0.entity.shortname}'.format(self)

    def __repr__(self):
        return '{0.name}'.format(self)


class Source(Base):
    """ Data Sources """
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    content = Column(String(25))
    url = Column(String)
    api = Column(String)
    units = Column(String(25))
    metrics = relationship('Metric', back_populates='source')

    def __str__(self):
        return 'Source:[{0.id}]:{0.name}:{0.content}:web={0.url}:{0.api}:#metrics={1}'.format(self, len(self.metrics))


class EnablerImp(Base):
    """ Enablers configuration """
    __tablename__ = 'enablers'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    owner_id = Column(Integer, ForeignKey('owners.id'))
    owner = relationship('Owner', back_populates='implementations')
    chapter = Column(String)
    type = Column(String)
    status = Column(String)
    metrics = relationship('Metric', back_populates='enabler_imp')

    def __str__(self):
        return 'IEnabler:[{0.id}]:{0.name}:{0.owner.name}:{0.chapter}:{0.type}:{0.status}:{0.metrics}]'.format(self)


class Metric(Base):
    """ Metrics defined for the sources """
    __tablename__ = 'metrics'
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'))
    source = relationship('Source', back_populates='metrics')
    enabler_id = Column(Integer, ForeignKey('enablers.id'))
    enabler_imp = relationship('EnablerImp', back_populates='metrics')
    measurements = relationship('Measurement', back_populates='metric')
    details = Column(PickleType)
    # details = Column(String)

    def __str__(self):
        return 'Metric:[{0.id}]:{0.source.name}:{0.enabler_imp.name}:{0.details}:m={1}'\
            .format(self, len(self.measurements))

    def __repr__(self):
        return '<{0.id}:{0.source.name}>'.format(self)


class Measurement(Base):
    """ Values read for enablers from sources by using their APIs """
    __tablename__ = 'measurements'
    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey('metrics.id'))
    metric = relationship('Metric', back_populates='measurements')
    date = Column(DateTime)
    value = Column(String)

    def __str__(self):
        return '{0.id}:{0.metric.source.name}:{0.metric.enabler_imp.name}:v={0.value}:d={1}'\
            .format(self, str(self.date))

    def __repr__(self):
        return '<{0.id}:{0.value}:{1}>'.format(self, str(self.date))
