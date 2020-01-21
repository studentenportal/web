# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from bs4 import BeautifulSoup
from model_bakery import baker

from apps.documents import models, forms


User = get_user_model()


def login(self):
    assert self.client.login(username='testuser', password='test')


class DocumentDownloadTest(TestCase):
    def setUp(self):
        # setUpClass
        baker.make_recipe('apps.front.user')

    def testSummaryServed(self):
        """Assert that the summaries get served, even without login."""
        doc = baker.make_recipe('apps.documents.document_summary')
        url = reverse('documents:document_download', args=(doc.category.name, doc.pk))
        response = self.client.get(url)
        assert response.status_code == 200

    def testExamRequireLogin(self):
        """Assert that the exams require login."""
        doc = baker.make_recipe('apps.documents.document_exam')
        url = reverse('documents:document_download', args=(doc.category.name, doc.pk))
        response = self.client.get(url)
        category_path = reverse('documents:document_list', args=(doc.category.name.lower(),))
        self.assertRedirects(response, '/accounts/login/?next=%s' % category_path)

    def testExamServed(self):
        """Assert that the exams get served when logged in."""
        login(self)
        doc = baker.make_recipe('apps.documents.document_exam')
        url = reverse('documents:document_download', args=(doc.category.name, doc.pk))
        response = self.client.get(url)
        assert response.status_code == 200

    def testUmlautDocumentServed(self):
        """Test whether documents with umlauts in their original filename can
        be served."""
        doc = baker.make_recipe('apps.documents.document_summary', original_filename='Füübäär Søreņ')
        url = reverse('documents:document_download', args=(doc.category.name, doc.pk))
        response = self.client.get(url)
        assert response.status_code == 200


class DocumentcategoryListViewTest(TestCase):
    def setUp(self):
        # setUpClass
        baker.make_recipe('apps.front.user')
        baker.make_recipe('apps.documents.document_summary')
        baker.make_recipe('apps.documents.document_summary')
        baker.make_recipe('apps.documents.document_exam')
        baker.make_recipe('apps.documents.document_software')
        baker.make_recipe('apps.documents.document_learning_aid')
        # setUp
        self.response = self.client.get(reverse('documents:documentcategory_list'))

    def testTitle(self):
        self.assertContains(self.response, '<h1>Dokumente</h1>')

    def testModuleName(self):
        """Test whether the module An1I appears in the list."""
        self.assertContains(self.response, '<em class="abbreviation">An1I</em>')
        self.assertContains(self.response, 'Analysis 1 für Informatiker')

    def testUserAddButton(self):
        """Test whether the add button is shown when and only when the user is logged in."""
        self.assertNotContains(self.response, 'Modul hinzufügen')
        login(self)
        logged_in_response = self.client.get(reverse('documents:documentcategory_list'))
        self.assertContains(logged_in_response, 'Modul hinzufügen')

    def testCounts(self):
        """Test whether the category counts are correct."""
        self.assertContains(self.response, '<span class="icon-doc"></span>2 Zusammenfassungen')
        self.assertContains(self.response, '<span class="icon-test"></span>1 Prüfung')
        self.assertContains(self.response, '<span class="icon-doc-alt"></span>2 Andere')


class DocumentcategoryAddViewTest(TestCase):
    taburl = '/dokumente/add/'

    def setUp(self):
        baker.make_recipe('apps.front.user')
        login(self)

    def testLoginRequired(self):
        self.client.logout()
        response = self.client.get(self.taburl)
        self.assertRedirects(response, '/accounts/login/?next=%s' % self.taburl)

    def testTitle(self):
        response = self.client.get(self.taburl)
        self.assertContains(response, 'Modul hinzufügen')

    def testAdd(self):
        data = {
            'name': 'Prog2',
            'description': 'Programmieren 2',
        }
        response1 = self.client.post(self.taburl, data)
        self.assertRedirects(response1, '/dokumente/')
        response2 = self.client.get('/dokumente/prog2/')
        self.assertContains(response2, '<h1>Dokumente Prog2</h1>')

    def testAddInvalid(self):
        dc_form = forms.DocumentCategoryForm({'name': u'MöKomÄP', 'description': u'MoKomAP with invalid name'})
        assert not dc_form.is_valid()
        dc_form = forms.DocumentCategoryForm({'name': u'MoKomAP', 'description': u'MoKomAP with valid name'})
        assert dc_form.is_valid()

    def testAddDuplicate(self):
        """Test whether DocumentCategory name field is unique"""
        models.DocumentCategory.objects.create(name='test', description='Test category')
        dc_form = forms.DocumentCategoryForm({'name': 'test', 'description': 'Another test category'})
        assert not dc_form.is_valid()

    def testAddInsensitiveDuplicate(self):
        """Test whether DocumentCategory name field is unique in any case"""
        models.DocumentCategory.objects.create(name='test', description='Test category')
        dc_form = forms.DocumentCategoryForm({'name': 'Test', 'description': 'Another test category'})
        assert not dc_form.is_valid()


class DocumentListViewTest(TestCase):
    def setUp(self):
        # setUpClass
        self.user1 = baker.make_recipe('apps.front.user')
        self.user2 = baker.make(User, first_name='Another', last_name='Guy', flattr='guy')
        self.doc1 = baker.make_recipe('apps.documents.document_summary',
                name='Analysis 1 Theoriesammlung',
                description='Theorie aus dem AnI1-Skript auf 8 Seiten',
                uploader=self.user1,
                upload_date='2011-12-18 01:28:52',
                change_date='2011-12-18 01:28:52',
                license=5)
        self.doc2 = baker.make_recipe('apps.documents.document_summary',
                uploader=self.user2, name='Title with Flattr')
        self.doc3 = baker.make_recipe('apps.documents.document_exam', uploader=self.user1)
        self.doc4 = baker.make_recipe('apps.documents.document_software', uploader=self.user1)
        self.doc5 = baker.make_recipe('apps.documents.document_learning_aid', uploader=self.user1)
        self.doc6 = baker.make_recipe('apps.documents.document_summary',
                uploader=self.user2, name='Title Noflattr', flattr_disabled=True)
        self.category = self.doc1.category
        # setUp
        self.url = reverse('documents:document_list', args=(self.category.name.lower(),))
        self.response = self.client.get(self.url)

    def testTitle(self):
        self.assertContains(self.response, '<h1>Dokumente An1I</h1>')

    def testDocumentTitle(self):
        soup = BeautifulSoup(self.response.content, 'html.parser')
        div_details = soup.find('h3', text='Analysis 1 Theoriesammlung').find_parent('div').prettify()
        assert '<h3 property="dct:title" xmlns:dct="http://purl.org/dc/terms/">\n  Analysis 1 Theoriesammlung\n </h3>' in div_details
        assert '<span class="label-summary">\n   Zusammenfassung\n  </span>' in div_details

    def testDocumentLicense(self):
        soup = BeautifulSoup(self.response.content, 'html.parser')
        div_details = soup.find('h3', text='Analysis 1 Theoriesammlung').find_parent('div').prettify()
        assert '<a href="http://creativecommons.org/licenses/by-nc-sa/3.0/deed.de" rel="license" ' + \
                      u'title="Veröffentlicht unter der CC BY-NC-SA 3.0 Lizenz">' in div_details
        assert ' <span class="label-license">\n    CC BY-NC-SA 3.0\n   </span>' in div_details

    def testDocumentFlattr(self):
        soup = BeautifulSoup(self.response.content, 'html.parser')
        div_flattr = soup.find('h3', text='Title with Flattr').find_parent('div').prettify()
        div_noflattr = soup.find('h3', text='Title Noflattr').find_parent('div').prettify()
        assert 'Flattr this' in div_flattr
        assert 'Flattr this' not in div_noflattr

    def testUploaderName(self):
        self.assertContains(self.response, 'Another Guy')

    def testDescription(self):
        self.assertContains(self.response, 'Theorie aus dem AnI1-Skript auf 8 Seiten')

    def testUploadDate(self):
        self.assertContains(self.response, '18.12.2011')

    def testEditButtonLoggedOut(self):
        url = reverse('documents:document_edit', args=(self.doc1.category.name.lower(), self.doc1.pk))
        self.assertNotContains(self.response, 'href="{}"'.format(url))

    def testEditButtonLoggedIn(self):
        login(self)
        url1 = reverse('documents:document_edit', args=(self.doc1.category.name.lower(), self.doc1.pk))
        url2 = reverse('documents:document_edit', args=(self.doc2.category.name.lower(), self.doc2.pk))
        response = self.client.get(self.url)
        self.assertContains(response, 'href="{}"'.format(url1))
        self.assertNotContains(response, 'href="{}"'.format(url2))

    def testDeleteButtonLoggedOut(self):
        url = reverse('documents:document_delete', args=(self.doc1.category.name.lower(), self.doc1.pk))
        self.assertNotContains(self.response, 'href="{}"'.format(url))

    def testDeleteButtonLoggedIn(self):
        login(self)
        url1 = reverse('documents:document_delete', args=(self.doc1.category.name.lower(), self.doc1.pk))
        url2 = reverse('documents:document_delete', args=(self.doc2.category.name.lower(), self.doc2.pk))
        response = self.client.get(self.url)
        self.assertContains(response, 'href="{}"'.format(url1))
        self.assertNotContains(response, 'href="{}"'.format(url2))

    def testDownloadCount(self):
        doc = baker.make_recipe('apps.documents.document_summary')
        dl_url = reverse('documents:document_download', args=(doc.category.name.lower(), doc.pk))

        # No downloads yet
        response0 = self.client.get(self.url)
        soup0 = BeautifulSoup(response0.content, 'html.parser')
        anchor0 = soup0.find('a', href=dl_url)
        document0 = anchor0.find_parent('article').prettify()
        assert "0 Downloads" in document0

        # First download
        self.client.get(dl_url)
        response1 = self.client.get(self.url)
        soup1 = BeautifulSoup(response1.content, 'html.parser')
        anchor1 = soup1.find('a', href=dl_url)
        document1 = anchor1.find_parent('article').prettify()
        assert "1 Download" in document1

        # Second download. Downloadcount shouldn't increase, as request was
        # done from the same IP
        self.client.get(dl_url)
        response2 = self.client.get(self.url)
        soup2 = BeautifulSoup(response2.content, 'html.parser')
        anchor2 = soup2.find('a', href=dl_url)
        document2 = anchor2.find_parent('article').prettify()
        assert "1 Download" in document2

    def testNullValueUploader(self):
        """Test whether a document without an uploader does not raise an error."""
        doc = baker.make_recipe('apps.documents.document_summary',
                name='Analysis 1 Theoriesammlung',
                description='Dieses Dokument ist eine Zusammenfassung der',
                uploader=None)
        url = reverse('documents:document_list', args=(doc.category.name.lower(),))
        response = self.client.get(url)
        self.assertContains(response, 'Analysis 1 Theoriesammlung')
        self.assertContains(response, 'Dieses Dokument ist eine Zusammenfassung der')
