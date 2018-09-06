#!/usr/bin/env python3
"""Dump all listed resource/x-bb-file from user-specified courses
using Blackboard Learn APIs. Works for CUHK(SZ).
"""

from getpass import getpass
import requests
from bs4 import BeautifulSoup
import base64
import json
import os
import functools

BB_DOMAIN = 'https://bb.cuhk.edu.cn'
BB_MOBILE_API = BB_DOMAIN + '/webapps/Bb-mobile-BBLEARN'
LOGIN_URL = BB_DOMAIN + '/webapps/login/'
COURSES_URL = BB_MOBILE_API + '/enrollments?course_type=COURSE'
SPECIFIC_COURSE_URL = BB_DOMAIN + '/learn/api/public/v1/courses/'
CONTENTS_URL = SPECIFIC_COURSE_URL + '{}/contents?courseId={}'
OBJECT_URL = SPECIFIC_COURSE_URL + '{}/contents/{}?courseId={}&contentId={}'
CHILDREN_URL = SPECIFIC_COURSE_URL + '{}/contents/{}/children?courseId={}&contentId={}'
ATTACHMENTS_URL = SPECIFIC_COURSE_URL + '{}/contents/{}/attachments?courseId={}&contentId={}'
ATTACHMENT_DL_URL = SPECIFIC_COURSE_URL + '{}/contents/{}/attachments/{}/download\
?courseId={}&contentId={}&attachmentId={}'

EXPORT_PATH = 'new_courses'
#COURSES = ['_237_1', '_245_1', '_110_1', '_113_1', '_112_1']
COURSES = []

makedirs = functools.partial(os.makedirs, exist_ok=True)

def auth():
    user_eid = input('Username:')
    user_password = getpass('Password:')

    session = requests.Session()
    # generate payload
    login_page = session.get(LOGIN_URL)
    login_page_content = BeautifulSoup(login_page.content, 'html.parser')
    tstring = login_page_content.find('input', attrs={'name':'tstring'})['value']
    b64pwd = base64.b64encode(user_password.encode('ascii'))
    # authenticate the session
    session.post(LOGIN_URL, data={
        'pstring': b64pwd,
        'tstring': tstring,
        'user_id': user_eid})
    return session

def logged_in(session):
    courses_page = session.get(COURSES_URL)
    courses_page_content = BeautifulSoup(courses_page.content, 'html.parser')
    if courses_page_content.mobileresponse['status'] == 'OK':
        print('Logged in.')
        return True
    else:
        print('Login failed: {}'.format(courses_page_content.mobileresponse['status']))
        return False

def dl(session, current_path, cid, oid, attachments):
    for object in attachments:
        attachment_path = os.path.join(current_path, object['fileName'])
        try:
            with open(attachment_path, 'xb') as destination:
                download = session.get(ATTACHMENT_DL_URL.format(cid, oid, object['id'], cid, oid, object['id']))
                print('  Get:', object['fileName'])
                destination.write(download.content)
        except FileExistsError:
            # file already exists, don't download again
            print('  Hit:', object['fileName'])
            pass

def dfs(session, current_path, cid, results):
    for object in results:
        obj_type = object['contentHandler']['id']
        #has_children = object['hasChildren'] # Bool
        available = object['availability']['available'] # str: 'Yes' or 'No'
        if available == 'Yes' and obj_type == 'resource/x-bb-folder': # TO DO; Learing-unit
            new_path = os.path.join(current_path, object['title'])
            makedirs(new_path)
            print(' Entering', object['title'])
            children_raw = session.get(CHILDREN_URL.format(cid, object['id'], cid, object['id']))
            children = json.loads(children_raw.content)['results']
            dfs(session, new_path, cid, children)
        if available == 'Yes' and obj_type == 'resource/x-bb-file':
            attachments_raw = session.get(ATTACHMENTS_URL.format(cid, object['id'], cid, object['id']))
            attachments = json.loads(attachments_raw.content)['results']
            dl(session, current_path, cid, object['id'], attachments)

def main():
    session = auth()
    while not logged_in(session):
        session = auth()
    makedirs(EXPORT_PATH)
    # TODO: fetch enrolled courses
    # print('Getting course list')
    for course in COURSES:
        course_info_raw = session.get(SPECIFIC_COURSE_URL + course, params={'courseId': course})
        course_info = json.loads(course_info_raw.content)
        course_path = os.path.join(EXPORT_PATH, course_info['name'])
        print('Searching', course_info['name'])
        # make directory for course
        makedirs(course_path)
        # list of contents
        course_contents_raw = session.get(CONTENTS_URL.format(course,course))
        course_contents = json.loads(course_contents_raw.content)['results']
        dfs(session, course_path, course, course_contents)
    print('Exit')

if __name__ == "__main__":
    main()
