Writing RESTful Web Services with Flask
=======================================

[![Build Status](https://travis-ci.org/miguelgrinberg/api-pycon2014.png?branch=master)](https://travis-ci.org/miguelgrinberg/api-pycon2014)

This repository contains a fully working API project that utilizes the techniques that I discussed in my PyCon 2014 talk on building beautiful APIs with Flask.

The API in this example implements a "students and classes" system and demonstrates RESTful principles, CRUD operations, error handling, user authentication, pagination, rate limiting and HTTP caching controls.

Requirements
------------

To install and run this application you need:

- Python 2.7 or 3.3+
- virtualenv
- git (only to clone this repository, you can download the code as a [zip file](https://github.com/miguelgrinberg/api-pycon2014/archive/master.zip) if you prefer)

Installation
------------

The commands below install the application and its dependencies:

    $ git clone https://github.com/miguelgrinberg/api-pycon2014.git
    $ cd api-pycon2014
    $ virtualenv venv
    $ . venv/bin/activate
    (venv) pip install -r requirements.txt

Note for Microsoft Windows users: replace the virtual environment activation command above with `venv\Scripts\activate`.

The core dependencies are Flask, Flask-HTTPAuth, Flask-SQLAlchemy, Flask-Script and redis (only used for the rate limiting feature). For unit tests nose and coverage are used. The httpie command line HTTP client is also installed as a convenience.

Unit Tests
----------

To ensure that your installation was successful you can run the unit tests:

    (venv) $ python manage.py test
    test_bad_auth (tests.test_api.TestAPI) ... ok
    test_cache_control (tests.test_api.TestAPI) ... ok
    test_classes (tests.test_api.TestAPI) ... ok
    test_etag (tests.test_api.TestAPI) ... ok
    test_pagination (tests.test_api.TestAPI) ... ok
    test_password_auth (tests.test_api.TestAPI) ... ok
    test_rate_limits (tests.test_api.TestAPI) ... ok
    test_registrations (tests.test_api.TestAPI) ... ok
    test_students (tests.test_api.TestAPI) ... ok
    
    Name                     Stmts   Miss Branch BrMiss  Cover   Missing
    --------------------------------------------------------------------
    api                          0      0      0      0   100%
    api.app                     13      0      5      1    94%
    api.auth                    13      0      2      0   100%
    api.decorators              84      1     26      1    98%   17
    api.errors                  31      9      0      0    71%   15-18, 29-32, 36-39
    api.helpers                 23      6     11      6    65%   11, 18-20, 27, 34
    api.models                  86      2      4      1    97%   48, 118
    api.rate_limit              38      1      6      1    95%   38
    api.token                   18      2      2      1    85%   15, 21
    api.v1_0                    20      3      2      0    86%   11, 16, 21
    api.v1_0.classes            36      0      0      0   100%
    api.v1_0.registrations      25      0      0      0   100%
    api.v1_0.students           36      0      0      0   100%
    --------------------------------------------------------------------
    TOTAL                      423     24     58     11    93%
    ----------------------------------------------------------------------
    Ran 9 tests in 4.378s
    
    OK

The report printed below the tests is a summary of the test coverage. A more detailed report is written to a `cover` folder. To view it, open `cover/index.html` with your web browser.

User Registration
-----------------

The API can only be accessed by authenticated users. New users can be registered with the application from the command line:

    (venv) $ python manage.py adduser <username>
    Password: <password>
    Confirm: <password>
    User <username> was registered successfully.

The system supports multiple users, so the above command can be run as many times as needed with different usernames. Users are stored in the application's database, which by default uses the SQLite engine. An empty database is created in the current folder if a previous database file is not found.

API Documentation
-----------------

The API supported by this application contains three top-level resources:

- `/api/v1.0/students/`: The collection of students.
- `/api/v1.0/classes/`: The collection of classes.
- `/api/v1.0/registrations/`: The collection of student/class registrations.

All other resource URLs are to be discovered from the responses returned from the above three.

There are four resource types supported by this API, described in the sections below. Note that this API supports resource representations in JSON format only.

### Resource Collections

All resource collections have the following structure:

    {
        "urls": [
            [URL 1],
            [URL 2],
            ...
        ],
        "meta": {
            "page": [current_page],
            "pages": [total_page_count],
            "per_page": [items_per_page],
            "total": [total item count],
            "prev": [link to previous page],
            "next": [link to next page],
            "first": [link to first page],
            "last": [link to last page]
        }
    }

The `urls` key contains an array with the URLs of the requested resources. Note that results are paginated, so not all the resource in the collection might be returned. Clients should use the navigation links in the `meta` portion to obtain more resources.

### Student Resource

A student resource has the following structure:

    {
        "url": [student URL],
        "name": [student name],
        "registrations": [link to student registrations]
    }

When creating or updating a student resource only the `name` field needs to be provided. The following example creates a student resource by sending a `POST` request to the top-level students URL. The `httpie` command line client is used to send this request.

    (venv) $ http --auth <username> POST http://localhost:5000/api/v1.0/students/ name=david
    http: password for <username>@localhost:5000: <password>
    HTTP/1.0 201 CREATED
    Content-Length: 2
    Content-Type: application/json
    Date: Fri, 04 Apr 2014 00:53:44 GMT
    Location: http://localhost:5000/api/v1.0/students/1
    Server: Werkzeug/0.9.4 Python/2.7
    
    {}

Only the `name` field needs to be provided when creating or modifying a student resource. Note the `Location` header included in the response, which contains the URL of the newly created resource. This URL can now be used to get specific information about this resource:

    (venv) $ http --auth <username> GET http://localhost:5000/api/v1.0/students/1
    http: password for <username>@localhost:5000: <password>
    HTTP/1.0 200 OK
    Content-Length: 157
    Content-Type: application/json
    Date: Fri, 04 Apr 2014 00:54:02 GMT
    ETag: "c65dfd7eef67b79e15a614c800009830"
    Server: Werkzeug/0.9.4 Python/2.7
    
    {
        "name": "david",
        "registrations": "http://localhost:5000/api/v1.0/students/1/registrations/",
        "url": "http://localhost:5000/api/v1.0/students/1"
    }

The student resource supports `GET`, `POST`, `PUT` and `DELETE` methods.

### Class Resource

The class resource has a similar structure:

    {
        "url": [class URL],
        "name": [class name],
        "registrations": [link to class registrations]
    }

Using `httpie` a class can be created as follows:

    (venv) $ http --auth <username> POST http://localhost:5000/api/v1.0/classes/ name=algebra
    http: password for <username>@localhost:5000: <password>
    HTTP/1.0 201 CREATED
    Content-Length: 2
    Content-Type: application/json
    Date: Fri, 04 Apr 2014 00:53:44 GMT
    Location: http://localhost:5000/api/v1.0/classes/1
    Server: Werkzeug/0.9.4 Python/2.7

    {}

Once again, the URL for the new resource is given in the `Location` header.

The class resource supports `GET`, `POST`, `PUT` and `DELETE` methods.

### Registration Resource

The registration resource associates a student with a class. Below is the structure of this resource:

    {
        "url": [registration URL],
        "student": [student URL],
        "class": [class URL],
        "timestamp": [date of registration]
    }

To create a registration a `POST` request to the top-level registration URL is sent:

    (venv) $ http --auth <username> POST http://localhost:5000/api/v1.0/registrations/ student=http://localhost:5000/api/v1.0/students/1 class=http://localhost:5000/api/v1.0/classes/1
    http: password for <username>@localhost:5000: <password>
    HTTP/1.0 201 CREATED
    Content-Length: 2
    Content-Type: application/json
    Date: Fri, 04 Apr 2014 01:05:50 GMT
    Location: http://localhost:5000/api/v1.0/registrations/1/1
    Server: Werkzeug/0.9.4 Python/2.7
    
    {}

The only required fields to create a registration resource are `student` and `class`, which should be set to the resource URLs for the respective student and class resources. The `timestamp` field is assigned automatically based on the clock at the time the request is sent.

Using the URL returned in the `Location` header now the registration resource can be queried:

    (venv) $ http --auth <username> GET http://localhost:5000/api/v1.0/registrations/1/1
    http: password for miguel@localhost:5000: <password>
    HTTP/1.0 200 OK
    Content-Length: 227
    Content-Type: application/json
    Date: Fri, 04 Apr 2014 01:06:14 GMT
    ETag: "512ece33e166ba6759ad31d913adfe17"
    Server: Werkzeug/0.9.4 Python/2.7

    {
        "url": "http://localhost:5000/api/v1.0/registrations/1/1",
        "student": "http://localhost:5000/api/v1.0/students/1",
        "class": "http://localhost:5000/api/v1.0/classes/1",
        "timestamp": "Fri, 04 Apr 2014 01:05:50 GMT"
    }

The registration resource supports `GET`, `POST` and `DELETE` methods.

Using Token Authentication
--------------------------

The default configuration uses username and password for request authentication. To switch to token based authentication the configuration stored in `config.py` must be edited. In particular, the line that begins with `USE_TOKEN_AUTH` must be changed to:

    USE_TOKEN_AUTH = True 

After this change restart the application for the change to take effect.

With this change authenticating using username and password will not work anymore. Instead an authentication token must be requested:

    (venv) $ http --auth <username> GET http://localhost:5000/auth/request-token
    http: password for <username>@localhost:5000: <password>
    HTTP/1.0 200 OK
    Cache-Control: no-cache, no-store, max-age=0
    Content-Length: 139
    Content-Type: application/json
    Date: Fri, 04 Apr 2014 01:18:55 GMT
    Server: Werkzeug/0.9.4 Python/2.7
    
    {
        "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTM5NjU3NzkzNSwiaWF0IjoxMzk2NTc0MzM1fQ.eyJpZCI6MX0.8XFUzlGz5XPGJp0weoOXy6avwr7OS1ojMbJYpBvw42I"
    }

The returned token must be sent as authentication for all requests into the API:

    (venv) $ http --auth eyJhbGciOiJIUzI1NiIsImV4cCI6MTM5NjU3NzkzNSwiaWF0IjoxMzk2NTc0MzM1fQ.eyJpZCI6MX0.8XFUzlGz5XPGJp0weoOXy6avwr7OS1ojMbJYpBvw42I: GET http://localhost:5000/api/v1.0/students/
    HTTP/1.0 200 OK
    Content-Length: 345
    Content-Type: application/json
    Date: Fri, 04 Apr 2014 01:21:52 GMT
    ETag: "b6ce14e7c7496c7d3b22fff0f0fba666"
    Server: Werkzeug/0.9.4 Python/2.7
    
    {
        "urls": [
            "http://localhost:5000/api/v1.0/students/1"
        ],
        "meta": {
            "page": 1,
            "pages": 1,
            "per_page": 50,
            "total": 1,
            "prev": null,
            "next": null,
            "first": "http://localhost:5000/api/v1.0/students/?per_page=50&page=1",
            "last": "http://localhost:5000/api/v1.0/students/?per_page=50&page=1"
        }
    }

Note the colon character following the token, this is to prevent `httpie` from asking for a password, since token authentication does not require one.

HTTP Caching
------------

The different API endpoints are configured to respond using the appropriate caching directives. The `GET` requests return an `ETag` header that HTTP caches can use with the `If-Match` and `If-None-Match` headers.

The `GET` request that returns the authentication token is not supposed to be cached, so the response includes a `Cache-Control` directive that disables caching.

Rate Limiting
-------------

This API supports rate limiting as an optional feature. To use rate limiting the application must have access to a Redis server running on the same host and listening on the default port.

To enable rate limiting change the following line in `config.py`:

    USE_RATE_LIMITS = True

The default configuration limits clients to 5 API calls per 15 second interval. When a client goes over the limit a response with the 429 status code is returned immediately, without carrying out the request. The limit resets as soon as the current 15 second period ends.

When rate limiting is enabled all responses return three additional headers:

    X-RateLimit-Limit: [period in seconds]
    X-RateLimit-Remaining: [remaining calls in this period]
    X-RateLimit-Reset: [time when the limits reset, in UTC epoch seconds]

Conclusion
----------

I hope you find this example useful. If you have any questions feel free to ask!

