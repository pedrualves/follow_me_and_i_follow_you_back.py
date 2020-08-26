from builtins import set
import requests
from requests.auth import HTTPBasicAuth
import string


def ask_credentials() -> (string, string):
    github_user = input('Please input your github login:\n')
    github_access_token = input('Please input your github access token:\n')
    return github_user, github_access_token


def fetch_by_type(type_request: string, github_user: string, github_access_token: string) -> list:
    has_more_elements = True
    page = 0
    logins = []

    while has_more_elements:
        page += 1
        r = requests.get('https://api.github.com/users/%s/%s?per_page=100&page=%s' % (github_user, type_request, page),
                         auth=HTTPBasicAuth(github_user, github_access_token))

        if r.status_code == 200:
            if len(r.json()) == 0:
                has_more_elements = False

            for r in r.json():
                logins.append(r['login'])
        else:
            raise Exception(r.json()['message'])

    return logins


def follow(users_to_follow: list, github_user: string, github_access_token: string):
    for user in users_to_follow:
        r = requests.put('https://api.github.com/user/following/%s' % user,
                         auth=HTTPBasicAuth(github_user, github_access_token))
        if r.status_code == 204:
            print('following %s' % user)
        else:
            raise Exception(r.json()['message'])


def unfollow(users_to_unfollow: list, github_user: string, github_access_token: string):
    for user in users_to_unfollow:
        r = requests.delete('https://api.github.com/user/following/%s' % user,
                            auth=HTTPBasicAuth(github_user, github_access_token))
        if r.status_code == 204:
            print('unfollowing %s' % user)
        else:
            raise Exception(r.json()['message'])


def report(following, followers) -> (list, list):
    i_follow_but_not_follow_me = sorted(following - followers)
    follow_me_but_i_not_following = sorted(followers - following)

    print('i_follow_but_not_follow_me: %s and they are: %s' % (
        len(i_follow_but_not_follow_me), i_follow_but_not_follow_me))
    print('follow_me_but_im_not_following: %s and they are %s' % (
        len(follow_me_but_i_not_following), follow_me_but_i_not_following))
    return i_follow_but_not_follow_me, follow_me_but_i_not_following


def ask_to_thanos(i_follow_but_not_follow_me: list, follow_me_but_i_not_following: list, github_user: string,
                  github_access_token: string):
    snap = input('Do you want Thanos to snap your fingers?(y/n)')

    if snap == 'y':
        follow(follow_me_but_i_not_following, github_user, github_access_token)
        unfollow(i_follow_but_not_follow_me, github_user, github_access_token)

    print('bye bye')


GITHUB_USER, GITHUB_ACCESS_TOKEN = ask_credentials()

followers = set(fetch_by_type('followers', GITHUB_USER, GITHUB_ACCESS_TOKEN))
following = set(fetch_by_type('following', GITHUB_USER, GITHUB_ACCESS_TOKEN))

i_follow_but_not_follow_me, follow_me_but_i_not_following = report(following, followers)

ask_to_thanos(i_follow_but_not_follow_me, follow_me_but_i_not_following, GITHUB_USER, GITHUB_ACCESS_TOKEN)
