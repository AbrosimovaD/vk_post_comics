import requests
from pathlib import Path
import random
from dotenv import load_dotenv
import os


def get_last_comic_number():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def download_image(url, path, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(Path(path, filename), 'wb') as file:
        file.write(response.content)


def get_upload_url(access_token, group_id, vers):
    params = {
        'access_token': access_token,
        'v': vers,
        'group_id': group_id
        }
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return response.json()['response']['upload_url']


def upload_photo_to_server(url, path, filename):
    with open(Path(path, filename), 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return response.json()


def upload_photo(access_token, group_id, vers, photo, server, hash):
    params = {
        'access_token': access_token,
        'v': vers,
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': hash
        }
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.get(url, params=params)
    response.raise_for_status()
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    owner_id = str(decoded_response['response'][0]['owner_id'])
    photo_id = str(decoded_response['response'][0]['id'])
    photo_name = f'photo{owner_id}_{photo_id}'
    return photo_name


def post_comic(photo_name, access_token, group_id, vers, comic_comment):
    url = 'https://api.vk.com/method/wall.post'
    params = {
        'access_token': access_token,
        'v': vers,
        'attachments': photo_name,
        'owner_id': - int(group_id),
        'from_group': 1,
        'message': comic_comment
    }
    response = requests.get(url, params=params)
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    response.raise_for_status()


def main():
    load_dotenv()
    access_token = os.environ['VK_ACCESS_TOKEN']
    group_id = os.environ['VK_GROUP_ID']
    last_comic_number = get_last_comic_number()
    comic_number = random.randint(1, last_comic_number)
    comic_url = f'https://xkcd.com/{comic_number}/info.0.json'
    comic_response = requests.get(comic_url)
    comic_response.raise_for_status()
    image_filename = 'comic.png'
    path_for_comic = Path(Path.home(), 'comic')
    comic = comic_response.json()
    url_for_image = comic['img']
    comic_comment = comic['alt']
    vers = '5.131'
    path_for_comic.mkdir(parents=True, exist_ok=True)
    try:
        download_image(url_for_image, path_for_comic, image_filename)
        upload_url = get_upload_url(access_token, group_id, vers)
        post_photo_params = upload_photo_to_server(upload_url, path_for_comic, image_filename)
        photo_name = upload_photo(access_token, group_id, vers, post_photo_params['photo'], post_photo_params['server'], post_photo_params['hash'])
        post_comic(photo_name, access_token, group_id, vers, comic_comment)
    finally:
        Path(path_for_comic, image_filename).unlink(missing_ok=True)


if __name__ == '__main__':
    main()
