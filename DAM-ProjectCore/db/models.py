#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import datetime
import enum
import logging
import os
from _operator import and_
from builtins import getattr
from urllib.parse import urljoin

import falcon
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Unicode, \
    UnicodeText, Table, type_coerce, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_i18n import make_translatable

import messages
from db.json_model import JSONModel
import settings

mylogger = logging.getLogger(__name__)

SQLAlchemyBase = declarative_base()
make_translatable(options={"locales": settings.get_accepted_languages()})


def _generate_media_url(class_instance, class_attibute_name, default_image=False):
    class_base_url = urljoin(urljoin(urljoin("http://{}".format(settings.STATIC_HOSTNAME), settings.STATIC_URL),
                                     settings.MEDIA_PREFIX),
                             class_instance.__tablename__ + "/")
    class_attribute = getattr(class_instance, class_attibute_name)
    if class_attribute is not None:
        return urljoin(urljoin(urljoin(urljoin(class_base_url, class_attribute), str(class_instance.id) + "/"),
                               class_attibute_name + "/"), class_attribute)
    else:
        if default_image:
            return urljoin(urljoin(class_base_url, class_attibute_name + "/"), settings.DEFAULT_IMAGE_NAME)
        else:
            return class_attribute


def _generate_media_path(class_instance, class_attibute_name):
    class_path = "/{0}{1}{2}/{3}/{4}/".format(settings.STATIC_URL, settings.MEDIA_PREFIX, class_instance.__tablename__,
                                              str(class_instance.id), class_attibute_name)
    return class_path


class GenereEnum(enum.Enum):
    male = "M"
    female = "F"


class EventTypeEnum(enum.Enum):
    hackathon = "H"
    lanparty = "LP"
    livecoding = "LC"


class EventStatusEnum(enum.Enum):
    open = "O"
    closed = "C"
    ongoing = "G"
    undefined = "U"


class UserToken(SQLAlchemyBase):
    __tablename__ = "users_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(Unicode(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="tokens")


class User(SQLAlchemyBase, JSONModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    username = Column(Unicode(50), nullable=False, unique=True)
    password = Column(UnicodeText, nullable=False)
    email = Column(Unicode(255), nullable=False)

    name = Column(Unicode(50), nullable=False)
    surname = Column(Unicode(50), nullable=False)
    birthdate = Column(Date)
    genere = Column(Enum(GenereEnum), nullable=False)
    phone = Column(Unicode(50))
    photo = Column(Unicode(255))


    tokens = relationship("UserToken", back_populates="user", cascade="all, delete-orphan")
    user_juego = relationship("Juego", back_populates = "juego_user")



    @hybrid_property
    def public_profile(self):
        return {
            "created_at": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
            "username": self.username,
            "genere": self.genere.value,
            "photo": self.photo,
        }

    @hybrid_property
    def photo_url(self):
        return _generate_media_url(self, "photo")

    @hybrid_property
    def photo_path(self):
        return _generate_media_path(self, "photo")

    @hybrid_method
    def set_password(self, password_string):
        self.password = pbkdf2_sha256.hash(password_string)

    @hybrid_method
    def check_password(self, password_string):
        return pbkdf2_sha256.verify(password_string, self.password)

    @hybrid_method
    def create_token(self):
        if len(self.tokens) < settings.MAX_USER_TOKENS:
            token_string = binascii.hexlify(os.urandom(25)).decode("utf-8")
            aux_token = UserToken(token=token_string, user=self)
            return aux_token
        else:
            raise falcon.HTTPBadRequest(title=messages.quota_exceded, description=messages.maximum_tokens_exceded)

    @hybrid_property
    def json_model(self):
        return {
            "created_at": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "surname": self.surname,
            "birthdate": self.birthdate.strftime(
                settings.DATE_DEFAULT_FORMAT) if self.birthdate is not None else self.birthdate,
            "genere": self.genere.value,
            "phone": self.phone,
            "photo": self.photo_url
        }



class Carta(SQLAlchemyBase, JSONModel):
    __tablename__ = "carta"
    id = Column(Integer, primary_key = True)
    numero = Column(Integer)
    palo = Column(Integer)


    #Relacio Carta Baraja
    baraja_id = Column(Integer, ForeignKey("baraja.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    carta_baraja = relationship("Baraja", back_populates="baraja_carta")

    @hybrid_property
    def json_model(self):
        return {
            "id": self.id,
            "numero": self.numero,
            "palo": self.palo

        }


class Baraja(SQLAlchemyBase, JSONModel):
    __tablename__ = "baraja"
    id = Column(Integer, primary_key=True)
    numCartas = Column(Integer)

    #Relacio Carta Baraja
    baraja_carta= relationship("Carta", back_populates="carta_baraja" )
    baraja_juego = relationship("Juego", back_populates = "juego_baraja")

    juego_id = Column(Integer, ForeignKey("juego.id"), nullable=False)

    @hybrid_property
    def json_model(self):
        return {
            "id": self.id,
            "numCartas": self.numCartas,

        }


class Juego(SQLAlchemyBase, JSONModel):
    __tablename__ = "juego"
    id = Column(Integer, primary_key = True, autoincrement = True)
    #win = Column(Boolean)
    puntuacio = Column(Integer, default = 0)

    jugador_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    juego_baraja = relationship("Baraja", back_populates = "baraja_juego")
    juego_user = relationship("User", back_populates = "user_juego")

    
    @hybrid_property
    def json_model(self):
        return {
            "id": self.id,
            "puntuacio": self.puntuacio,
            "jugador_id": self.jugador_id

        }
