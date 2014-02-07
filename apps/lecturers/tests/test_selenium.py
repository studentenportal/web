# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import time

from selenium.webdriver.firefox.webdriver import WebDriver

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from django.conf import settings

from model_mommy import mommy

from apps.lecturers import models


class QuoteTest(LiveServerTestCase):

    def setUp(self):
        mommy.make_recipe('apps.front.user')
        mommy.make_recipe('apps.front.lecturer')
        mommy.make(models.Quote, quote='spam', comment='ham')

        self.browser = WebDriver()
        self.login(username='testuser', password='test')

    def tearDown(self):
        self.browser.quit()

    def login(self, username, password):
        self.open(settings.LOGIN_URL)
        self.browser.find_element_by_id("id_username").send_keys("testuser")
        self.browser.find_element_by_id("id_password").send_keys("test")
        self.browser.find_element_by_css_selector("input.btn.btn-primary").click()

    def open(self, url):
        self.browser.get("%s%s" % (self.live_server_url, url))

    def testUpvoteIncreasesVoteCount(self):
        context = "//div[@id='content']/table/tbody/tr[1]/td/div/"
        vote_count = lambda: int(self.browser.find_element_by_xpath(context + "/span").text)
        upvote = lambda: self.browser.find_element_by_xpath(context + "/div").click()

        #Arrange
        self.open(reverse('lecturers:quote_list'))
        self.assertEqual(0, vote_count())
        #Act
        upvote()
        time.sleep(0.5)
        #Assert
        self.assertEqual(1, vote_count())
