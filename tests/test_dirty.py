#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, timedelta

from imageporndirtyrubot.dirty import get_last_domain_posts, raw_request
from imageporndirtyrubot.exception import APIException


class TestDirtyApi(unittest.TestCase):
    """
    Functional test for get_last_domain_posts
    """

    def test_small_amount(self):
        posts = get_last_domain_posts('historyporn', limit=3)
        self.assertEqual(len(posts), 3)

    def test_multipage_and_during_last_time(self):
        posts = get_last_domain_posts('historyporn', limit=100)
        self.assertEqual(len(posts), 100)

        sixth_post_timestamp = posts[66]['created']
        utc_now_timestamp = int(datetime.utcnow().strftime("%s"))
        seconds_since_66th_post = utc_now_timestamp - sixth_post_timestamp
        posts = get_last_domain_posts('historyporn', limit=100, time_inverval=seconds_since_66th_post)
        self.assertEqual(len(posts), 66)


class TestDirtyExceptions(unittest.TestCase):
    """
    Test for correct exception raising
    """

    def test_incorrect_uri(self):
        with self.assertRaises(APIException):
            raw_request('/posts/delete/all/', 'post')

    def test_incorrect_method(self):
        with self.assertRaises(AttributeError):
            raw_request('/posts/', 'blow')

    # TODO incorrect AUTH


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
