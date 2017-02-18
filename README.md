# Slightly evil password strength checker

Checks how strong your user's password is via questionably ethical means.

## Usage

Please don't actually use this.

```python
>>> from evilpass import check_pass
>>> check_pass("password", "email address", "username")
['A computer could guess this password in less than a second',
 'Add another word or two. Uncommon words are better.']

>>> check_pass("P455WorD", "email address", "username")
['A computer could guess this password in 12 seconds',
 'Add another word or two. Uncommon words are better.',
 "Predictable substitutions like '@' instead of 'a' don't help very much."]

>>> check_pass("correct-horse-battery-staple", "email address", "username")
[]
```

## Password reuse is bad, okay?

So quit doing it. Use a password manager. I personally recommend
[pass](https://www.passwordstore.org/).

## Side note

I suggest not trying to log into your user's account on other sites.

## Future development

* Automate use of proxies to avoid rate limiting and other things external
  services might do when they detect you're doing this
* Add other external services to check (I spent about 5 minutes on Google before
  I decided it wasn't worth the time required to reverse engineer their login
  flow, but it might be the most valuable account to try)
* ~~Store valid credentials in a database for evil purposes~~

https://www.xkcd.com/792/
