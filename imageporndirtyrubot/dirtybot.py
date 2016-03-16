# -*- coding: utf-8 -*-
import os
from io import BytesIO
from string import Template

import click
import pytimeparse
import requests
from PIL import Image

from imageporndirtyrubot import dirty, google
from imageporndirtyrubot.dirty import DirtyCantLoginException
from imageporndirtyrubot.google import GoogleCaptchaAPIException


def find_and_post_higher_resolution_images(
    username, password, domain, template,
    limit, time_limit, min_rating, max_size,
    min_increase, skip_posts_with_my_comments
):

    min_increase = 1 + min_increase/100.0

    dirty_auth = dirty.get_auth_headers(username, password)
    latest_domain_posts = dirty.get_last_domain_posts(
        domain,
        auth_headers=dirty_auth,
        time_inverval=time_limit, # TODO NOT WORKING
        limit=limit,
        threshold_rating=min_rating
    )

    for post in latest_domain_posts:
        data = post.get('data', {})
        media = data.get('media')
        if not data.get('type') == 'link':
            continue

        link = data.get('link', {})

        if media and media.get('type') == 'image':
            # Link post wih attecjed image
            image_size = (media.get('width'), media.get('height'))
            image_url = media.get('url')
        elif not media and link.get('type') == 'image':
            continue
            # No posts with small images
            image_url = link.get('url')
            try:
                image = Image.open(BytesIO(requests.get(image_url).content))
            except IOError:
                continue
        else:
            continue

        if skip_posts_with_my_comments:
            my_comment_found = False
            for comment in dirty.get_post_comments(post['id'], auth_headers=dirty_auth):
                if comment.get('user', {}).get('login') == username:
                    my_comment_found = True
                    break

            if my_comment_found:
                continue

        new_image_url, new_image_size = google.find_higher_resolution_image(
            media.get('url'),
            min_width=media.get('width') * min_increase,
            min_height=media.get('height') * min_increase
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
    template_path = options.get('template_path')
    if not template_path:
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'comment.tpl')

    with open(template_path, 'r') as f:
        template = Template(f.read())

    try:
        find_and_post_higher_resolution_images(
            username=username,
            password=password,
            domain=domain,
            template=template,
            limit=options.get('limit'),
            time_limit=options.get('time_limit'),
            min_rating=options.get('min_rating'),
            max_size=options.get('max_size'),
            min_increase=options.get('min_increase'),
            skip_posts_with_my_comments=options.get('skip_commented')
        )
    except DirtyCantLoginException:
        show_error('Incorrect username or password')
    except GoogleCaptchaAPIException:
        show_error('Google asks for CAPTCHA, try to open http://www.google.com in your browser')


def show_error(msg):
    click.secho(msg, err=True, fg='red')
