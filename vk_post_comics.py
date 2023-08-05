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
    Path(path).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    with open(f'{path}/{filename}', 'wb') as file:
        file.write(response.content)


def get_upload_url(params):
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status
    return response.json()['response']['upload_url']


def post_photo_to_server(url, path, filename):
    with open(f'{path}/{filename}', 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
    return response.json()


def upload_photo(params, post_params):
    params['photo'] = post_params['photo']
    params['server'] = post_params['server']
    params['hash'] = post_params['hash']
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.get(url, params=params)
    response.raise_for_status()
    upload_response = response.json()['response'][0]
    photo_name = 'photo' + str(upload_response['owner_id']) + '_' + str(upload_response['id']) + '&access_key=' + upload_response['access_key']
    return photo_name


def post_comic(photo_name, params, comic_comment):
    url = 'https://api.vk.com/method/wall.post?'
    params['attachments'] = photo_name
    params['owner_id'] = -int(params['group_id'])
    del params['group_id']
    params['from_group'] = 1
    params['message'] = comic_comment
    response = requests.get(url, params=params)
    response.raise_for_status()


def main():
    load_dotenv()
    access_token = os.environ['VK_ACCESS_TOKEN']
    group_id = os.environ['VK_GROUP_ID']
    last_comic_number = get_last_comic_number()
    comic_number = random.randint(1, last_comic_number)
    url_for_comic = f'https://xkcd.com/{comic_number}/info.0.json'
    comic = requests.get(url_for_comic)
    comic.raise_for_status()
    filename_for_image = 'comic.png'
    path_for_comic = 'D://comic'
    url_for_image = comic.json()['img']
    comic_comment = comic.json()['alt']
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': '5.131'
    }
    download_image(url_for_image, path_for_comic, filename_for_image)
    upload_url = get_upload_url(params)
    post_photo_params = post_photo_to_server(upload_url, path_for_comic, filename_for_image)
    photo_name = upload_photo(params, post_photo_params)
    post_comic(photo_name, params, comic_comment)
    Path(f'{path_for_comic}/{filename_for_image}').unlink(missing_ok=True)


if __name__ == '__main__':
    main()
