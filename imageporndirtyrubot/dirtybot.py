# -*- coding: utf-8 -*-
from io import BytesIO
from string import Template

import click
import pytimeparse
import requests
from PIL import Image

from imageporndirtyrubot import dirty, google
from imageporndirtyrubot.exception import APIException


DEFAULT_TEMPLATE = u"""\
Я нашел картинку лучшего качества: <a href="${image_url}">url</a> (${width} x ${height})
<img src="${image_url}">
Это сообщение опубликовано <a href="https://github.com/ilyatikhonov/imageporndirtyrubot">роботом</a>, который призван помочь найти картинки лучшего качества.
"""


def find_and_post_higher_resolution_images(
    username, password, domain, template_path,
    limit, time_limit, min_rating, max_size,
    min_increase, skip_posts_with_my_comments
):

    if template_path:
        with open(template_path, 'r') as f:
            template = Template(f.read())
    else:
        template = Template(DEFAULT_TEMPLATE)

    min_increase = 1 + min_increase/100.0

    dirty_auth = dirty.get_auth_headers(username, password)
    latest_domain_posts = dirty.get_last_domain_posts(
        domain,
        auth_headers=dirty_auth,
        time_inverval=time_limit,
        limit=limit,
        threshold_rating=min_rating
    )

    for post in latest_domain_posts:
        if post['data']['type'] != 'link':
            continue

        if post['data']['link'] and post['data']['link']['thumbnails']:
            thumbnails = post['data']['link']['thumbnails']
        elif post['data']['media'] and post['data']['media']['thumbnails']:
            thumbnails = post['data']['media']['thumbnails']
        else:
            continue

        src_image_url = thumbnails['original']['url']
        src_width = thumbnails['original']['width']
        src_height = thumbnails['original']['height']

        if skip_posts_with_my_comments:
            for comment in dirty.get_post_comments(post['id'], auth_headers=dirty_auth):
                if comment.get('user', {}).get('login') == username:
                    # комментарий найден, проходим мимо
                    continue

        new_image_url, new_image_size = google.find_higher_resolution_image(
            src_image_url,
            min_width=src_width * min_increase,
            min_height=src_height * min_increase
        )

        if not new_image_url:
            # Higher resolution image is not found
            continue

        # Yep! Larger image is found
        comment_body = template.substitute(
            image_url=new_image_url,
            width=new_image_size[0],
            height=new_image_size[1]
        )
        dirty.create_comment(post['id'], comment_body, auth_headers=dirty_auth)
        click.secho('[готово] {}.dirty.ru/{}-{}'.format(post['domain']['prefix'], post['url_slug'], post['id']), fg='green')


@click.command()
@click.option('-u', '--username', prompt='Your dirty name, sir')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-d', '--domain', prompt=True)
@click.option('-t', '--template_path', type=click.Path(dir_okay=False, exists=True))
@click.option('-l', '--limit',  default=100, type=click.IntRange(min=1))
@click.option('-c', '--time_limit', default='24h', callback=lambda ctx, param, value: pytimeparse.parse(value))
@click.option('-r', '--min_rating')
@click.option('-s', '--max_size', type=click.IntRange(min=1), default=3000,
              help="Posts with larger images (width or height) will not been processed")
@click.option('-i', '--min_increase', type=click.IntRange(min=1), default=20,
              help="Post new image only if it larger than original at least in given percentage")
@click.option('--skip_commented', default=True, type=click.BOOL,
              help="Skip posts where current user already made a comment")
@click.option('-v', '--verbose', count=True)
def imageporndirtyrubot(username, password, domain, **options):
    try:
        find_and_post_higher_resolution_images(
            username=username,
            password=password,
            domain=domain,
            template_path=options.get('template_path'),
            limit=options.get('limit'),
            time_limit=options.get('time_limit'),
            min_rating=options.get('min_rating'),
            max_size=options.get('max_size'),
            min_increase=options.get('min_increase'),
            skip_posts_with_my_comments=options.get('skip_commented')
        )
    except APIException as e:
        click.secho(str(e), err=True, fg='red')
