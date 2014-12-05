import unittest
from werkzeug.exceptions import BadRequest
from .test_client import TestClient
from api.app import create_app
from api.models import db, User
from api.errors import ValidationError


class TestAPI(unittest.TestCase):
    default_username = 'dave'
    default_password = 'cat'

    def setUp(self):
        self.app = create_app('test_config')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        u = User(username=self.default_username,
                 password=self.default_password)
        db.session.add(u)
        db.session.commit()
        self.client = TestClient(self.app, u.generate_auth_token(), '')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_password_auth(self):
        self.app.config['USE_TOKEN_AUTH'] = False
        good_client = TestClient(self.app, self.default_username,
                                 self.default_password)
        rv, json = good_client.get('/api/v1.0/students/')
        self.assertTrue(rv.status_code == 200)

        self.app.config['USE_TOKEN_AUTH'] = True
        u = User.query.get(1)
        good_client = TestClient(self.app, u.generate_auth_token(), '')
        rv, json = good_client.get('/api/v1.0/students/')
        self.assertTrue(rv.status_code == 200)

    def test_bad_auth(self):
        bad_client = TestClient(self.app, 'abc', 'def')
        rv, json = bad_client.get('/api/v1.0/students/')
        self.assertTrue(rv.status_code == 401)

        self.app.config['USE_TOKEN_AUTH'] = True
        bad_client = TestClient(self.app, 'bad_token', '')
        rv, json = bad_client.get('/api/v1.0/students/')
        self.assertTrue(rv.status_code == 401)

    def test_students(self):
        # get collection
        rv, json = self.client.get('/api/v1.0/students/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['urls'] == [])

        # create new
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'susan'})
        self.assertTrue(rv.status_code == 201)
        susan_url = rv.headers['Location']

        # get
        rv, json = self.client.get(susan_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'susan')
        self.assertTrue(json['url'] == susan_url)

        # create new
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'david'})
        self.assertTrue(rv.status_code == 201)
        david_url = rv.headers['Location']

        # get
        rv, json = self.client.get(david_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'david')
        self.assertTrue(json['url'] == david_url)

        # create bad request
        rv,json = self.client.post('/api/v1.0/students/', data={})
        self.assertTrue(rv.status_code == 400)

        self.assertRaises(ValidationError, lambda:
            self.client.post('/api/v1.0/students/',
                             data={'not-name': 'david'}))

        # modify
        rv, json = self.client.put(david_url, data={'name': 'david2'})
        self.assertTrue(rv.status_code == 200)

        # get
        rv, json = self.client.get(david_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'david2')

        # get collection
        rv, json = self.client.get('/api/v1.0/students/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(susan_url in json['urls'])
        self.assertTrue(david_url in json['urls'])
        self.assertTrue(len(json['urls']) == 2)

        # delete
        rv, json = self.client.delete(susan_url)
        self.assertTrue(rv.status_code == 200)

        # get collection
        rv, json = self.client.get('/api/v1.0/students/')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(susan_url in json['urls'])
        self.assertTrue(david_url in json['urls'])
        self.assertTrue(len(json['urls']) == 1)

    def test_classes(self):
        # get collection
        rv, json = self.client.get('/api/v1.0/classes/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['urls'] == [])

        # create new
        rv, json = self.client.post('/api/v1.0/classes/',
                                    data={'name': 'algebra'})
        self.assertTrue(rv.status_code == 201)
        algebra_url = rv.headers['Location']

        # get
        rv, json = self.client.get(algebra_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'algebra')
        self.assertTrue(json['url'] == algebra_url)

        # create new
        rv, json = self.client.post('/api/v1.0/classes/',
                                    data={'name': 'lit'})
        self.assertTrue(rv.status_code == 201)
        lit_url = rv.headers['Location']

        # get
        rv, json = self.client.get(lit_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'lit')
        self.assertTrue(json['url'] == lit_url)

        # create bad
        rv,json = self.client.post('/api/v1.0/classes/', data={})
        self.assertTrue(rv.status_code == 400)

        self.assertRaises(ValidationError, lambda:
            self.client.post('/api/v1.0/classes/', data={'not-name': 'lit'}))

        # modify
        rv, json = self.client.put(lit_url, data={'name': 'lit2'})
        self.assertTrue(rv.status_code == 200)

        # get
        rv, json = self.client.get(lit_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['name'] == 'lit2')

        # get collection
        rv, json = self.client.get('/api/v1.0/classes/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(algebra_url in json['urls'])
        self.assertTrue(lit_url in json['urls'])
        self.assertTrue(len(json['urls']) == 2)

        # delete
        rv, json = self.client.delete(lit_url)
        self.assertTrue(rv.status_code == 200)

        # get collection
        rv, json = self.client.get('/api/v1.0/classes/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(algebra_url in json['urls'])
        self.assertFalse(lit_url in json['urls'])
        self.assertTrue(len(json['urls']) == 1)

    def test_registrations(self):
        # create new students
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'susan'})
        self.assertTrue(rv.status_code == 201)
        susan_url = rv.headers['Location']

        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'david'})
        self.assertTrue(rv.status_code == 201)
        david_url = rv.headers['Location']

        # create new classes
        rv, json = self.client.post('/api/v1.0/classes/',
                                    data={'name': 'algebra'})
        self.assertTrue(rv.status_code == 201)
        algebra_url = rv.headers['Location']

        rv, json = self.client.post('/api/v1.0/classes/',
                                    data={'name': 'lit'})
        self.assertTrue(rv.status_code == 201)
        lit_url = rv.headers['Location']

        # register students to classes
        rv, json = self.client.post('/api/v1.0/registrations/',
                                    data={'student': susan_url,
                                          'class': algebra_url})
        self.assertTrue(rv.status_code == 201)
        susan_in_algebra_url = rv.headers['Location']

        rv, json = self.client.post('/api/v1.0/registrations/',
                                    data={'student': susan_url,
                                          'class': lit_url})
        self.assertTrue(rv.status_code == 201)
        susan_in_lit_url = rv.headers['Location']

        rv, json = self.client.post('/api/v1.0/registrations/',
                                    data={'student': david_url,
                                          'class': algebra_url})
        self.assertTrue(rv.status_code == 201)
        david_in_algebra_url = rv.headers['Location']

        # get registration
        rv, json = self.client.get(susan_in_lit_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['student'] == susan_url)
        self.assertTrue(json['class'] == lit_url)

        # get collection
        rv, json = self.client.get('/api/v1.0/registrations/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(susan_in_algebra_url in json['urls'])
        self.assertTrue(susan_in_lit_url in json['urls'])
        self.assertTrue(david_in_algebra_url in json['urls'])
        self.assertTrue(len(json['urls']) == 3)

        # bad registrations
        rv,json = self.client.post('/api/v1.0/registrations/', data={})
        self.assertTrue(rv.status_code == 400)

        self.assertRaises(ValidationError, lambda:
            self.client.post('/api/v1.0/registrations/',
                             data={'student': david_url}))

        self.assertRaises(ValidationError, lambda:
            self.client.post('/api/v1.0/registrations/',
                             data={'class': algebra_url}))

        self.assertRaises(ValidationError, lambda:
            self.client.post('/api/v1.0/registrations/',
                             data={'student': david_url, 'class': 'bad-url'}))

        self.assertRaises(ValidationError, lambda:
            self.client.post('/api/v1.0/registrations/',
                             data={'student': david_url,
                                   'class': algebra_url + '1'}))
        db.session.remove()

        # get classes from each student
        rv, json = self.client.get(susan_url)
        self.assertTrue(rv.status_code == 200)
        susans_reg_url = json['registrations']
        rv, json = self.client.get(susans_reg_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(susan_in_algebra_url in json['urls'])
        self.assertTrue(susan_in_lit_url in json['urls'])
        self.assertTrue(len(json['urls']) == 2)

        rv, json = self.client.get(david_url)
        self.assertTrue(rv.status_code == 200)
        davids_reg_url = json['registrations']
        rv, json = self.client.get(davids_reg_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(david_in_algebra_url in json['urls'])
        self.assertTrue(len(json['urls']) == 1)

        # get students for each class
        rv, json = self.client.get(algebra_url)
        self.assertTrue(rv.status_code == 200)
        algebras_reg_url = json['registrations']
        rv, json = self.client.get(algebras_reg_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(susan_in_algebra_url in json['urls'])
        self.assertTrue(david_in_algebra_url in json['urls'])
        self.assertTrue(len(json['urls']) == 2)

        rv, json = self.client.get(lit_url)
        self.assertTrue(rv.status_code == 200)
        lits_reg_url = json['registrations']
        rv, json = self.client.get(lits_reg_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(susan_in_lit_url in json['urls'])
        self.assertTrue(len(json['urls']) == 1)

        # unregister students
        rv, json = self.client.delete(susan_in_algebra_url)
        self.assertTrue(rv.status_code == 200)

        rv, json = self.client.delete(david_in_algebra_url)
        self.assertTrue(rv.status_code == 200)

        # get collection
        rv, json = self.client.get('/api/v1.0/registrations/')
        self.assertTrue(rv.status_code == 200)
        self.assertFalse(susan_in_algebra_url in json['urls'])
        self.assertTrue(susan_in_lit_url in json['urls'])
        self.assertFalse(david_in_algebra_url in json['urls'])
        self.assertTrue(len(json['urls']) == 1)

        # delete student
        rv, json = self.client.delete(susan_url)
        self.assertTrue(rv.status_code == 200)

        # get collection
        rv, json = self.client.get('/api/v1.0/registrations/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['urls']) == 0)
        
    def test_rate_limits(self):
        self.app.config['USE_RATE_LIMITS'] = True

        rv, json = self.client.get('/api/v1.0/registrations/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue('X-RateLimit-Remaining' in rv.headers)
        self.assertTrue('X-RateLimit-Limit' in rv.headers)
        self.assertTrue('X-RateLimit-Reset' in rv.headers)
        self.assertTrue(int(rv.headers['X-RateLimit-Limit']) == int(rv.headers['X-RateLimit-Remaining']) + 1)
        while int(rv.headers['X-RateLimit-Remaining']) > 0:
            rv, json = self.client.get('/api/v1.0/registrations/')
        self.assertTrue(rv.status_code == 429)

    def test_pagination(self):
        # create several students
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'one'})
        self.assertTrue(rv.status_code == 201)
        one_url = rv.headers['Location']
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'two'})
        self.assertTrue(rv.status_code == 201)
        two_url = rv.headers['Location']
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'three'})
        self.assertTrue(rv.status_code == 201)
        three_url = rv.headers['Location']
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'four'})
        self.assertTrue(rv.status_code == 201)
        four_url = rv.headers['Location']
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'five'})
        self.assertTrue(rv.status_code == 201)
        five_url = rv.headers['Location']

        # get collection in pages
        rv, json = self.client.get('/api/v1.0/students/?page=1&per_page=2')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(one_url in json['urls'])
        self.assertTrue(two_url in json['urls'])
        self.assertTrue(len(json['urls']) == 2)
        self.assertTrue('total' in json['meta'])
        self.assertTrue(json['meta']['total'] == 5)
        self.assertTrue('prev' in json['meta'])
        self.assertTrue(json['meta']['prev'] is None)
        first_url = json['meta']['first'].replace('http://localhost', '')
        last_url = json['meta']['last'].replace('http://localhost', '')
        next_url = json['meta']['next'].replace('http://localhost', '')

        rv, json = self.client.get(first_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(one_url in json['urls'])
        self.assertTrue(two_url in json['urls'])
        self.assertTrue(len(json['urls']) == 2)

        rv, json = self.client.get(next_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(three_url in json['urls'])
        self.assertTrue(four_url in json['urls'])
        self.assertTrue(len(json['urls']) == 2)
        next_url = json['meta']['next'].replace('http://localhost', '')

        rv, json = self.client.get(next_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(five_url in json['urls'])
        self.assertTrue(len(json['urls']) == 1)

        rv, json = self.client.get(last_url)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(five_url in json['urls'])
        self.assertTrue(len(json['urls']) == 1)

    def test_cache_control(self):
        client = TestClient(self.app, self.default_username,
                            self.default_password)
        rv, json = client.get('/auth/request-token')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue('Cache-Control' in rv.headers)
        cache = [c.strip() for c in rv.headers['Cache-Control'].split(',')]
        self.assertTrue('no-cache' in cache)
        self.assertTrue('no-store' in cache)
        self.assertTrue('max-age=0' in cache)
        self.assertTrue(len(cache) == 3)

    def test_etag(self):
        # create two students
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'one'})
        self.assertTrue(rv.status_code == 201)
        one_url = rv.headers['Location']
        rv, json = self.client.post('/api/v1.0/students/',
                                    data={'name': 'two'})
        self.assertTrue(rv.status_code == 201)
        two_url = rv.headers['Location']

        # get their etags
        rv, json = self.client.get(one_url)
        self.assertTrue(rv.status_code == 200)
        one_etag = rv.headers['ETag']
        rv, json = self.client.get(two_url)
        self.assertTrue(rv.status_code == 200)
        two_etag = rv.headers['ETag']

        # send If-None-Match header
        rv, json = self.client.get(one_url, headers={
            'If-None-Match': one_etag})
        self.assertTrue(rv.status_code == 304)
        rv, json = self.client.get(one_url, headers={
            'If-None-Match': one_etag + ', ' + two_etag})
        self.assertTrue(rv.status_code == 304)
        rv, json = self.client.get(one_url, headers={
            'If-None-Match': two_etag})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get(one_url, headers={
            'If-None-Match': two_etag + ', *'})
        self.assertTrue(rv.status_code == 304)

        # send If-Match header
        rv, json = self.client.get(one_url, headers={
            'If-Match': one_etag})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get(one_url, headers={
            'If-Match': one_etag + ', ' + two_etag})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client.get(one_url, headers={
            'If-Match': two_etag})
        self.assertTrue(rv.status_code == 412)
        rv, json = self.client.get(one_url, headers={
            'If-Match': '*'})
        self.assertTrue(rv.status_code == 200)

        # change a resource
        rv, json = self.client.put(one_url, data={'name': 'not-one'})
        self.assertTrue(rv.status_code == 200)

        # use stale etag
        rv, json = self.client.get(one_url, headers={
            'If-None-Match': one_etag})
        self.assertTrue(rv.status_code == 200)
