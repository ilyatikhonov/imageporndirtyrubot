from datetime import datetime

import requests

from imageporndirtyrubot.exception import APIException

DIRTY_API_PATH = 'https://dirty.ru/api'
# DIRTY_API_PATH = 'http://d3.dev/api'
MAX_PER_PAGE = 42


class DirtyCantLoginException(APIException):
    pass


def raw_request(uri, method, querystring=None, data=None, headers=None, **requests_options):
    """
    Make Dirty API HTTP request to given uri and return parsed JSON response.

    raises APIException for external API errors
    """
    if method == 'get':
        make_request = requests.get
    elif method == 'post':
        make_request = requests.post
    else:
        raise AttributeError('Unsupported request method: {}'.format(method))

    try:
        response = make_request(
            '{}{}'.format(DIRTY_API_PATH, uri),
            params=querystring,
            data=data,
            headers=headers,
            **requests_options
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise APIException('Dirty API Error: {}'.format(str(e)), http_code=e.response.status_code)


def unpaginate_raw_request(collection_name, limit, date_limit=None, *args, **kwargs):
    querystring = kwargs.pop('querystring', {})
    querystring['page'] = 1
    remaining = limit
    result = []

    while remaining > 0:
        per_page = min(MAX_PER_PAGE, remaining)
        querystring['per_page'] = per_page

        items = raw_request(querystring=querystring, *args, **kwargs).get(collection_name, [])
        valid_size = len(items)
        if date_limit:
            # count items that fits in date limmit
            valid_size = 0
            for elem in items:
                if elem['created'] <= date_limit:
                    break
                valid_size += 1

        result += items[:valid_size]
        if valid_size < per_page:
            # no more posts
            break
        remaining -= per_page
        querystring['page'] += 1

    return result


def get_auth_headers(username, password):
    """

    Raises: DirtyCantLogin, APIException
    Args:
        username:
        password:

    Returns:

    """
    try:
        response = raw_request('/auth/login/', 'post', data={'username': username, 'password': password})
    except APIException as e:
        if e.http_code == 403:
            raise DirtyCantLoginException()
        raise e

    return {
        'X-Futuware-UID': response['uid'],
        'X-Futuware-SID': response['sid']
    }


def get_last_domain_posts(domain_prefix, auth_headers=None, time_inverval=None, limit=100, threshold_rating=None):
    date_limit = None
    if time_inverval:
        date_limit = int(datetime.utcnow().strftime("%s")) - int(time_inverval)

    return unpaginate_raw_request(
        uri='/domains/{}/posts/'.format(domain_prefix),
        method='get',
        collection_name='posts',
        querystring={'sorting': 'date_created', 'threshold_rating': threshold_rating},
        headers=auth_headers,
        limit=limit,
        date_limit=date_limit
    )


def upload_image(file_name, auth_headers=None):
    """Upload image and return Media Data dict"""
    print("BB")
    return raw_request(
        '/images', 'post',
        headers=auth_headers,
        files={'file': open(file_name, 'rb')}
    )


def create_comment(post_id, body, media_id=None, parent_id=None, auth_headers=None):
    """Create comment on given post"""
    print("AAAA")
    return raw_request(
        '/posts/{}/comments/'.format(post_id), 'post',
        data={
            'body': body,
            'media_id': media_id,
            'parent_id': parent_id
        },
        headers=auth_headers
    )


def get_post_comments(post_id, auth_headers=None):
    """Return list of comments for given post"""
    return raw_request(
        '/posts/{}/comments/'.format(post_id),
        'get',
        headers=auth_headers
    ).get('comments', [])
