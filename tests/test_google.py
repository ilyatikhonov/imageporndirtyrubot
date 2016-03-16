#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from imageporndirtyrubot.exception import APIException
from imageporndirtyrubot.google import find_higher_resolution_image, GoogleCaptchaAPIException

TEST_IMAGE_URL = 'https://v1.std3.ru/500/90/fb/1455805029-90fb57f390b071bb67f72ab8da875afa.jpeg'


class TestFindHigherResoulutionImagesUsingGoogleImages(unittest.TestCase):
    def test_find_higher_resolution_images(self):
        try:
            url, size = find_higher_resolution_image(TEST_IMAGE_URL)
            self.assertIsNotNone(url, 'Found new image')

            url, size = find_higher_resolution_image(TEST_IMAGE_URL, min_width=size[0], min_height=size[1])
            self.assertIsNone(url, 'There is no bigger image')

        except GoogleCaptchaAPIException:
            raise unittest.SkipTest('Google requested CAPTCHA')

    def test_incorrect_image_url(self):
        try:
            with self.assertRaises(APIException):
                find_higher_resolution_image('not://an.url')
        except GoogleCaptchaAPIException:
            raise unittest.SkipTest('Google has requested CAPTCHA')


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
