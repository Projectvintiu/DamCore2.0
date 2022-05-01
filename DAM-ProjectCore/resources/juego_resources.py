import falcon
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Juego
from resources.base_resources import DAMCoreResource

class ResourceGetJuego(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetJuego, self).on_get(req, resp, *args, **kwargs)

        if "id_juego" in kwargs:
            try:
                response_juego = self.db_session.query(Juego).filter(Juego.id == kwargs["id_juego"]).one() #one per retornar 1 all per tots

                resp.media = response_juego.json_model
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.juego_doesnt_exist)
        else:
            raise falcon.HTTPMissingParam("id_juego")




class ResourceGetAllJuegosJugador(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetAllJuegosJugador, self).on_get(req, resp, *args, **kwargs)


        if "id_jugador" in kwargs:
            try:
                response_juego = self.db_session.query(Juego).filter(Juego.jugador_id == kwargs["id_jugador"]).all() #one per retornar 1 all per tots


                response_juegos = list()
                aux_juegos = self.db_session.query(Juego)


                if aux_juegos is not None:
                    for current_juego in aux_juegos.all():
                        #if current_juego.jugador_id == kwargs["id_jugador"]:
                        response_juegos.append(current_juego.json_model)

                resp.media = response_juegos
                resp.status = falcon.HTTP_200


            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.juego_doesnt_exist)
        else:
            raise falcon.HTTPMissingParam("id_jugador")


class ResourcesAddJuego(DAMCoreResource):
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourcesAddJuego, self).on_post(req, resp, *args, **kwargs)

        aux_juego = Juego()

        try:

            aux_juego.puntuacio = req.get_param("puntuacio")
            aux_juego.jugador_id = req.get_param("jugador_id")

            self.db_session.add(aux_juego)

            try:
                self.db_session.commit()
            except IntegrityError:
                raise falcon.HTTPBadRequest(description=messages.juego_exists)

        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)

        resp.status = falcon.HTTP_200