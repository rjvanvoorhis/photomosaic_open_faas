import time
import binascii
import requests
from io import BytesIO
import json
import os
from functools import partial
from photomosaic.scripts import create_photomosaic


class Environment(object):
    def __getattr__(self, key):
        return {k.lower(): v for k, v in os.environ.items()}.get(key)


def callback_function(idx, item, username):
    if max(idx, 1) % 3 != 0:
        return
    streamer = BytesIO()
    img = item.image_data.img.copy()
    img.thumbnail((300, 300))
    img.save(streamer, format='gif')
    streamer.seek(0)
    raw_data = streamer.read()
    streamer.close()
    encoded_data = encode_image_data(raw_data)
    total_frames = idx
    frame_directory = os.path.dirname(item.output_file)
    if os.path.exists(frame_directory):
        total_frames = len(os.listdir(frame_directory))
    # url = f'http://localhost:5000/api/v1/photomosaic/users/{username}/pending_json'
    url = f'{Environment().mosaic_api_url}/users/{username}/pending_json'
    payload = {
        'frame':
            {'mimetype': f'image/gif',
             'filename': item.output_file,
             'image_data': encoded_data},
        'progress': float(idx / max(1, total_frames)),
        'total_frames': total_frames
    }
    requests.patch(url, data=json.dumps(payload))


def make_file_path(extension='jpg'):
    return f'{str(time.time()).replace(".", "")}.{extension}'


def encode_image_data(image_data):
    return binascii.b2a_base64(image_data).decode()


def decode_image_data(image_string):
    return binascii.a2b_base64(image_string)


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    body = json.loads(req)
    image_data = decode_image_data(body['file'])

    filename = body['filename']
    username = body['username']
    tile_size = body.get('tile_size', 8)
    enlargement = body.get('enlargement', 1)
    url = f'{Environment().mosaic_api_url}/users/{username}/gallery'
    extension = 'gif' if filename.endswith('gif') else 'jpg'
    new_file = make_file_path(extension)
    alternate_file = make_file_path('gif') if extension == 'jpg' else None
    callback = partial(callback_function, username=username) if extension == 'gif' else None
    with open(new_file, 'wb') as fn:
        fn.write(image_data)
    create_photomosaic(new_file, output_file=new_file, save_intermediates=True, alternate_filename=alternate_file,
                       progress_callback=callback, tile_size=tile_size, enlargement=enlargement)
    msg = f'uploaded {new_file}'
    files = {'mosaic_file': (new_file, open(new_file, 'rb'), f'image/{extension}')}
    if alternate_file is not None:
        msg = f'{msg} and progress gif {alternate_file}'
        files['alternate_file'] = (alternate_file, open(alternate_file, 'rb'), 'image/gif')
    requests.post(url, files=files)
    for fp in [alternate_file, new_file]:
        if fp is not None and os.path.exists(fp):
            os.remove(fp)
    return {'message': msg, 'status': 201}
