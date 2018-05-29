import logging

import flask
from flask import Blueprint, Response, abort, current_app, request
from six.moves.urllib.parse import urljoin

from medallion import auth, error
from medallion.views import MEDIA_TYPE_TAXII_V20

logger = logging.getLogger(__name__)
mod = Blueprint('discovery', __name__)


@mod.route("/taxii/", methods=["GET"])
@auth.login_required
def get_server_discovery():
    # Having access to the discovery method is only related to having
    # credentials on the server. The metadata returned might be different
    # depending upon the credentials.
    server_discovery = current_app.medallion_backend.server_discovery()

    if not server_discovery or not server_discovery.get('title'):
        return error(404, "No discovery information available")

    # Allow the data to hold relative URLs so users can change the hostname/IP
    # that medallion is listening on without updating the data.
    if 'default' in server_discovery:
        server_discovery['default'] = urljoin(request.host_url, server_discovery['default'])
    if 'api_roots' in server_discovery:
        server_discovery['api_roots'] = [urljoin(request.host_url, x) for x in server_discovery['api_roots']]

    return Response(response=flask.json.dumps(server_discovery), status=200, mimetype=MEDIA_TYPE_TAXII_V20)


@mod.route("/<string:api_root>/", methods=["GET"])
@auth.login_required
def get_api_root_information(api_root):
    # TODO: Check if user has access to objects in collection.
    root_info = current_app.medallion_backend.get_api_root_information(api_root)

    if root_info:
        return Response(response=flask.json.dumps(root_info), status=200, mimetype=MEDIA_TYPE_TAXII_V20)
    abort(404)


@mod.route("/<string:api_root>/status/<string:id_>/", methods=["GET"])
@auth.login_required
def get_status(api_root, id_):
    # TODO: Check if user has access to objects in collection.
    status = current_app.medallion_backend.get_status(api_root, id_)

    if status:
        return Response(response=flask.json.dumps(status), status=200, mimetype=MEDIA_TYPE_TAXII_V20)
    abort(404)
