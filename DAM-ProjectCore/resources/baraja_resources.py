import falcon
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Baraja
from resources.base_resources import DAMCoreResource

class ResourceGetBaraja(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetBaraja, self).on_get(req, resp, *args, **kwargs)

        if "id_baraja" in kwargs:
            try:
                response_juego = self.db_session.query(Baraja).filter(Baraja.id == kwargs["id_baraja"]).one()

                resp.media = response_juego.json_model
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.juego_doesnt_exist)
        else:
            raise falcon.HTTPMissingParam("id_baraja")




class ResourceAddBaraja(DAMCoreResource):  #localhost:8000//baraja/add?id=2&numCartas=3&juego_id=1
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceAddBaraja, self).on_post(req, resp, *args, **kwargs)

        aux_baraja = Baraja()

        try:

            aux_baraja.id = req.get_param("id")
            aux_baraja.numCartas = req.get_param("numCartas")
            aux_baraja.juego_id = req.get_param("juego_id")

            self.db_session.add(aux_baraja)

            self.db_session.commit()

        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)

        resp.status = falcon.HTTP_200
