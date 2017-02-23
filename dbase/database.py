#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##
# Copyright 2017 FIWARE Foundation, e.V.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##
from sqlalchemy.orm.exc import NoResultFound
from dbase import db, Base, engine, Entity, Owner, Source, EnablerImp, Metric, Measurement
from config import entities, owners, sources, enablers, endpoints

__author__ = 'Fernando López'


class Database:
    def __init__(self):
        Base.metadata.create_all(engine)
        self.__entities__()
        self.__owners__()
        self.__sources__()
        self.__enablers__()
        self.__endpoints__()

    @staticmethod
    def __entities__():
        for params in entities:
            try:
                entity = db.query(Entity).filter_by(shortname=params['shortname']).one()
            except NoResultFound:
                db.add(Entity(**params))
            else:
                setattr(entity, 'name', params['name'])
        else:
            db.commit()

    @staticmethod
    def __owners__():
        for params in owners:
            try:
                entity = db.query(Entity).filter_by(shortname=params['entity']).one()
            except NoResultFound:
                raise
            else:
                params['entity_id'] = entity.id
                del params['entity']
                query = db.query(Owner).filter_by(name=params['name'])

                try:
                    owner = query.one()
                except NoResultFound:
                    db.add(Owner(**params))
                else:
                    for attr in ('shortname', 'email'):
                        if hasattr(owner, attr) and attr in params:
                            setattr(owner, attr, params[attr])
        else:
            db.commit()

    @staticmethod
    def __sources__():
        for params in sources:
            try:
                source = db.query(Source).filter_by(name=params['name']).one()
            except NoResultFound:
                db.add(Source(**params))
            else:
                for attr in ('content', 'url', 'api', 'units'):
                    if hasattr(source, attr) and attr in params:
                        setattr(source, attr, params[attr])
        else:
            db.commit()

    @staticmethod
    def __enablers__():
        for params in enablers:
            # print(params)
            try:
                owner = db.query(Owner).filter_by(name=params['owner']).one()
            except NoResultFound:
                raise
            else:
                params['owner_id'] = owner.id
                del params['owner']
                try:
                    enabler = db.query(EnablerImp).filter_by(name=params['name']).one()
                except NoResultFound:
                    db.add(EnablerImp(**params))
                else:
                    for attr in ('chapter', 'type', 'status'):
                        if hasattr(enabler, attr) and attr in params:
                            setattr(enabler, attr, params[attr])
        else:
            db.commit()

    @staticmethod
    def __endpoints__():
        for params in endpoints:
            # print(params)
            try:
                enabler = db.query(EnablerImp).filter_by(name=params['enabler']).one()
            except:
                raise
            else:
                m_params = {'enabler_id': enabler.id}
                for source in db.query(Source).all():
                    sourcename = source.name.lower()

                    if sourcename not in params:
                        continue

                    m_params['source_id'] = source.id
                    m_params['details'] = params[sourcename]

                    try:
                        metric = db.query(Metric).filter_by(source_id=source.id, enabler_id=enabler.id).one()
                    except NoResultFound:
                        db.add(Metric(**m_params))
                    else:
                        metric.details = m_params['details']
        else:
            db.commit()

    @staticmethod
    def show_data():
        print('\n>>> entities')
        my_entities = db.query(Entity).all()
        for entity in my_entities:
            print(entity)

        print('\n>>> owners')
        my_owners = db.query(Owner).all()
        for owner in my_owners:
            print(owner)

        print('\n>>> sources')
        my_sources = db.query(Source).all()
        for source in my_sources:
            print(source)

        print('\n>>> enablers')
        my_enablers = db.query(EnablerImp).all()
        for enabler in my_enablers:
            print(enabler)

        print('\n>>> metrics')
        my_metrics = db.query(Metric).all()
        for metric in my_metrics:
            print(metric)

        print('\n>>> measurements')
        my_measurements = db.query(Measurement).all()
        if len(my_measurements) == 0:
            print("No measurements yet")
        else:
            for measurement in my_measurements:
                print(measurement)
