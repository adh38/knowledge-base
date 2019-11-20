# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#
#   Adam Herbst 4/17/19
#
#   This is the file that handles requests.  ie. it initially serves the web page when someone
#   types the URL in a browser, and it responds to AJAX (real-time load/save requests)
#   triggered by the user while interacting with the page.
#
#   For a rundown of how web2py works:
#   http://web2py.com/books/default/chapter/29/03/overview#Simple-examples
#

from datetime import datetime


#   knowledge:
#   This is the main page.
#   https://adamdrewherbst.pythonanywhere.com/welcome/default/knowledge
#
#   For the content of the page, see /views/default/knowledge.html
#
#   Since this is the 'knowledge' handler of '/controllers/default.py', and since there is
#   also a /views/default/knowledge.html file, the user can append /default/knowledge to the
#   site URL.  This handler will then be run, which can optionally process the HTTP request variables
#   stored in the 'request' object, and whatever it returns will be passed to knowledge.html to
#   render the page for the user.  You can add a new page to the site in the same way.
#
def knowledge():

    #   make sure the global ROOT concept exists; this is the root of the tree of all concepts
    db['concept'].update_or_insert(id=1, name='ROOT', description='root of the concept tree')

    db['concept'].update_or_insert(id=2, name='is a', description='is an instance of')

    #   There are no URL options for the main page and knowledge.html handles everything so we just
    #   return an empty Python dictionary
    return dict()


#   AJAX HANDLERS & HELPER FUNCTIONS
#   The rest of the handlers are called by the JavaScript on the page, via AJAX.
#   They load and save records from the database.


def load():

    import json, urllib
    body = request.body.read()
    body = urllib.unquote(body).decode('utf8')
    request_vars = json.loads(body)
    concepts = request_vars['concepts']

    records = {'concept': {}, 'link': {}}

    loadConcept(1, records)
    loadConcept(2, records)

    return response.json(records)


def loadConcept(cid, records):

    if cid in records['concept']:
        return

    record = db.concept(cid)
    records['concept'][cid] = record.as_dict()

    for link in db((db.link.start == record.id) | (db.link.end == record.id)).iterselect():
        loadLink(link, records)


def loadLink(link, records):

    if link.id in records['link']:
        return

    records['link'][link.id] = link.as_dict()

    loadConcept(link.start, records)
    loadConcept(link.end, records)
    if link.concept is not None:
        loadConcept(link.concept, records)


def save():

    import json, urllib
    body = request.body.read()
    body = urllib.unquote(body).decode('utf8')
    request_vars = json.loads(body)
    records = request_vars['records']

    print('SAVING RECORDS')
    print('{}'.format(records))

    for cid in records['concept']:
        saveRecord('concept', records['concept'][cid])
    for lid in records['link']:
        link = records['link'][lid]
        for field in link:
            if link[field] in records['concept']:
                link[field] = records['concept'][link[field]]['id']
        saveRecord('link', link)

    db.executesql('alter table concept auto_increment=1')
    db.executesql('alter table link auto_increment=1')

    return response.json(records)


def saveRecord(table, record):

    if 'deleted' in record:
        db(db[table].id == record['id']).delete()
    elif 'id' in record:
        db[table][record['id']].update_record(**record)
    else:
        record['id'] = db[table].insert(**record)


def isint(val):
    try:
        int(val)
        return True
    except TypeError:
        return False
    except ValueError:
        return False

def positive(val):
    return isint(val) and int(val) > 0


#   This serves a test page I was using to learn how to display MathML.  Not needed by the main site
#   but useful for testing rendering of math symbols via MathML
#
def mathjax():
    return dict()



#   Below are the default handlers provided by web2py - these are not used right now but could be useful...
#   'index' in particular is the default page the user sees if they don't add the /default/knowledge URL suffix
#
# -------------------------------------------------------------------------
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to the Concept Graph!'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


