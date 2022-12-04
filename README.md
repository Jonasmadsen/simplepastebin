# SimplePastebin
A simple pastebin written in python

Is fully self contain and work continuously under light load for months.

This software is provided as is without any warranty. This is simply a small toy example to showcase python.

To run in prod use something similar to:

sudo apt-get install authbind
sudo touch /etc/authbind/byport/80
sudo chmod 500 /etc/authbind/byport/80
sudo chown USER /etc/authbind/byport/80

$ cd simplepastebin
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install . 
$ pip install gunicorn

authbind gunicorn --certfile selfsigned.crt --keyfile selfsigned.key --bind 0.0.0.0:443 'app:app' &