# SimplePastebin
A simple pastebin written in python

Is fully self contain and work continuously under light load for months.

This software is provided as is without any warranty. This is simply a small toy example to showcase python.

To run in prod use something similar to:

authbind gunicorn --certfile selfsigned.crt --keyfile selfsigned.key --bind 0.0.0.0:443 'app:app' &