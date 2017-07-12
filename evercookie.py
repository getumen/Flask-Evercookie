# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from flask import Blueprint, request, Response, send_file
import tempfile
import settings
from PIL import Image
from copy import deepcopy
from utils import crossdomain

app = Blueprint('evercookie', __name__)


@app.route('/api/cookie/cache')
@crossdomain(origin=settings.origin, methods=['GET'])
def evercookie_cache():
    if settings.cache_cookie_name in request.cookies:
        cookie = request.cookies.get(settings.cache_cookie_name)
        resp = Response(cookie)
        resp.headers['Content-Type'] = 'text/html; charset=UTF-8'
        resp.headers['Last-Modified'] = 'Wed, 30 Jun 2010 21:36:48 GMT'
        resp.headers['Expires'] = 'Tue, 31 Dec 2030 23:30:45 GMT'
        resp.headers['Cache-Control'] = 'private, max-age=630720000'
        resp.headers['Content-length'] = len(cookie)
        return resp
    else:
        return Response(status=304)


@app.route('/api/cookie/etag')
@crossdomain(origin=settings.origin, methods=['GET'])
def evercookie_etag():
    if settings.etag_cookie_name in request.cookies:
        cookie = settings.etag_cookie_name
        resp = Response(request.cookies.get(cookie))
        resp.headers['Content-Type'] = 'text/html; charset=UTF-8'
        resp.headers['ETag'] = cookie
        resp.headers['Content-length'] = len(cookie)
    else:
        if 'HTTP_IF_NONE_MATCH' in request.headers:
            cookie = request.headers.get('HTTP_IF_NONE_MATCH')
            resp = Response(cookie)
            resp.headers['ETag'] = cookie
            resp.headers['Content-length'] = len(cookie)
        else:
            resp = Response()
    return resp


@app.route('/api/cookie/png')
@crossdomain(origin=settings.origin, methods=['GET'])
def evercookie_png():
    if settings.png_cookie_name not in request.cookies:
        return Response(status=304)

    base_img = Image.new('RGB', (200, 1), color=None)
    cookie_value = list(request.cookies[settings.png_cookie_name])
    quotient, remainder = divmod(len(cookie_value), 3)
    new_cookie_value = deepcopy(cookie_value)

    if remainder == 1:
        new_cookie_value.extend(['\x00', '\x00'])
    elif remainder == 2:
        new_cookie_value.extend(['\x00'])

    x_axis = 0
    y_axis = 0
    index = 0
    image_obj = tempfile.TemporaryFile()

    while index < len(new_cookie_value):
        base_img.putpixel((x_axis, y_axis), (
        ord(new_cookie_value[index]), ord(new_cookie_value[index + 1]), ord(new_cookie_value[index + 2])))
        index += 3
        x_axis += 1

    base_img.save(image_obj, 'PNG')
    image_obj.seek(0, 0)
    resp = send_file(image_obj, mimetype="image/png")

    resp.headers['Last-Modified'] = 'Wed, 30 Jun 2010 21:36:48 GMT'
    resp.headers['Expires'] = 'Tue, 31 Dec 2030 23:30:45 GMT'
    resp.headers['Cache-Control'] = 'private, max-age=630720000'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
