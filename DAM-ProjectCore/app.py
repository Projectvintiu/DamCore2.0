#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging.config

import falcon

import messages
import middlewares
from falcon_multipart.middleware import MultipartMiddleware
from resources import account_resources, common_resources, user_resources, juego_resources, carta_resources, baraja_resources
from settings import configure_logging

# LOGGING
mylogger = logging.getLogger(__name__)
configure_logging()


# DEFAULT 404
# noinspection PyUnusedLocal
def handle_404(req, resp):
    resp.media = messages.resource_not_found
    resp.status = falcon.HTTP_404


# FALCON
app = application = falcon.API(
    middleware=[
        middlewares.DBSessionManager(),
        middlewares.Falconi18n(),
        MultipartMiddleware()
    ]
)
application.add_route("/", common_resources.ResourceHome())




application.add_route("/users/register", user_resources.ResourceRegisterUser())
application.add_route("/users/show/{username}", user_resources.ResourceGetUserProfile())

'''
application.add_route("/carta/show/{idCarta}", carta_resources.ResourceGetCarta)
application.add_route("/carta/add", carta_resources.ResourceAddCarta)
application.add_route("/carta", carta_resources.ResourceCarta)

application.add_route("/baraja/show/{idBaraja}", baraja_resources.ResourceGetBaraja)
application.add_route("/baraja", baraja_resources.ResourceCarta)
'''
application.add_route("/juego/show/{id_juego}", juego_resources.ResourceGetJuego())
application.add_route("/juego/shows/{id_jugador}", juego_resources.ResourceGetAllJuegosJugador())
application.add_route("/juego/add", juego_resources.ResourcesAddJuego())


application.add_route("/carta/show/{id_carta}", carta_resources.ResourceGetCarta())
application.add_route("/carta/add", carta_resources.ResourceAddCarta())

application.add_route("/baraja/show/{id_baraja}", baraja_resources.ResourceGetBaraja())
application.add_route("/baraja/add", baraja_resources.ResourceAddBaraja())


application.add_route("/account/profile", account_resources.ResourceAccountUserProfile())
application.add_route("/account/profile/update_profile_image", account_resources.ResourceAccountUpdateProfileImage())
application.add_route("/account/create_token", account_resources.ResourceCreateUserToken())
application.add_route("/account/delete_token", account_resources.ResourceDeleteUserToken())


#ALL partidas , getCarta, getBaralla addcarta addbaralla, mirar jugador, camp de win boolean o enum

application.add_sink(handle_404, "")
