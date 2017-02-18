import requests
import string
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from zxcvbn import zxcvbn

ZXCVBN_MINIMUM_SCORE = 3
ZXCVBN_MINIMUM_CRACK_TIME_DAYS = 7

def _get(url, session=None, **kwargs):
    headers = kwargs.get("headers") or dict()
    headers.update(requests.utils.default_headers())
    headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    kwargs["headers"] = headers
    if session:
        return session.get(url, **kwargs)
    else:
        return requests.get(url, **kwargs)

def _post(url, session=None, **kwargs):
    headers = kwargs.get("headers") or dict()
    headers.update(requests.utils.default_headers())
    headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    kwargs["headers"] = headers
    if session:
        return session.post(url, **kwargs)
    else:
        return requests.post(url, **kwargs)

def _check_twitter(username, email, pw):
    with requests.Session() as session:
        r = _get("https://mobile.twitter.com/login", session=session)
        tk = session.cookies.get("_mb_tk")
        if not tk or r.status_code != 200:
            r = _get("https://mobile.twitter.com/i/nojs_router?path=%2Flogin", session=session)
            r = _get("https://mobile.twitter.com/login", session=session)
            tk = session.cookies.get("_mb_tk")
        if not tk or r.status_code != 200:
            return False
        r = _post("https://mobile.twitter.com/sessions", data={
            "authenticity_token": tk,
            "session[username_or_email]": username,
            "session[password]": pw,
            "remember_me": 0,
            "wfa": 1,
            "redirect_after_login": "/home"
        }, session=session)
        url = urlparse(r.url)
        return url.path != "/login/error"

def _check_github(username, email, pw):
    with requests.Session() as session:
        r = _get("https://github.com/login", session=session)
        soup = BeautifulSoup(r.text, "html.parser")
        i = soup.select_one("input[name='authenticity_token']")
        token = i["value"]
        r = _post("https://github.com/session", session=session, data={
            "utf8": "✓",
            "commit": "Sign in",
            "authenticity_token": token,
            "login": username,
            "password": pw,
        })
        url = urlparse(r.url)
        return url.path != "/session" and url.path != "/login"

def _check_fb(username, email, pw):
    with requests.Session() as session:
        r = _get("https://www.facebook.com", session=session)
        if r.status_code != 200:
            return False
        r = _post("https://www.facebook.com/login.php?login_attempt=1&lwv=100", data={
            "email": email,
            "pass": pw,
            "legacy_return": 0,
            "timezone": 480,
        }, session=session)
        url = urlparse(r.url)
        return url.path != "/login.php"

def _check_reddit(username, email, pw):
    with requests.Session() as session:
        r = _get("https://www.reddit.com/login", session=session)
        if r.status_code != 200:
            return False
        r = _post("https://www.reddit.com/post/login", session=session, data={
                "op": "login",
                "dest": "https://www.reddit.com/",
                "user": username,
                "passwd": pw,
                "rem": "off"
            })
        return not "incorrect username or password" in text

def _check_hn(username, email, pw):
    r = _post("https://news.ycombinator.com", data={
        "goto": "news",
        "acct": username,
        "pw": pw
    }, allow_redirects=False)
    return r.status_code == 200 # Redirects on success

checks = {
    "Twitter": _check_twitter,
    "Facebook": _check_fb,
    "GitHub": _check_github,
    "Reddit": _check_reddit,
    "Hacker News": _check_hn
}

def check_pass(pw, email, username):
    errors = list()
    # benign part
    results = zxcvbn(pw, user_inputs=[email, username])

    brute_force_crack_time = results['crack_times_seconds']['online_no_throttling_10_per_second']

    if brute_force_crack_time < ZXCVBN_MINIMUM_CRACK_TIME_DAYS * 24 * 60 * 60:
        brute_force_display_string = results['crack_times_display']['online_no_throttling_10_per_second']
        errors.append("A computer could guess this password in " + brute_force_display_string)

    if results['score'] < ZXCVBN_MINIMUM_SCORE:
        for error in results['feedback']['suggestions']:
            errors.append(error)

    # evil part
    if not username:
        username = email
    for check in checks:
        try:
            if checks[check](email, username, pw):
                errors.append("Your password must not be the same as your {} password".format(check))
        except:
            pass
    return errors
