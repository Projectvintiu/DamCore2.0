import falcon
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Carta
from resources.base_resources import DAMCoreResource

class ResourceGetCarta(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetCarta, self).on_get(req, resp, *args, **kwargs)

        if "id_carta" in kwargs:
            try:
                response_juego = self.db_session.query(Carta).filter(Carta.id == kwargs["id_carta"]).one() #one per retornar 1 all per tots

                resp.media = response_juego.json_model
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.juego_doesnt_exist)
        else:
            raise falcon.HTTPMissingParam("id_carta")




class ResourceAddCarta(DAMCoreResource): #localhost:8000//carta/add?id=3&numero=3&palo=1&baraja_id=1
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceAddCarta, self).on_post(req, resp, *args, **kwargs)

        aux_carta = Carta()

        try:

            aux_carta.id = req.get_param("id")
            aux_carta.numero = req.get_param("numero")
            aux_carta.palo = req.get_param("palo")
            aux_carta.baraja_id = req.get_param("baraja_id")

            self.db_session.add(aux_carta)
            self.db_session.commit()

        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)

        resp.status = falcon.HTTP_200
