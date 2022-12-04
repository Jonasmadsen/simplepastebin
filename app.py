import datetime
import os.path
import shutil
import time

from flask import Flask, render_template, request, redirect

app = Flask(__name__)
max_paste_size = 512
message_folder = 'msg'
recent_file = message_folder + '/' + 'recent.txt'

# When to allow a poster to post again
recent_posters = list()
last_clear_of_recent_posters = datetime.datetime.now()
interval_between_recent_posters_clear = 5

# When to remove all messages
last_clear_of_all_msg = datetime.datetime.now()
clear_all_msg_interval = 600


def delete_all_msg_if_time():
    global last_clear_of_all_msg
    # Delete all msg if it is time
    if (datetime.datetime.now() - last_clear_of_all_msg).seconds > clear_all_msg_interval:
        shutil.rmtree(message_folder)
        last_clear_of_all_msg = datetime.datetime.now()


def ensure_dirs_exists(ip_str):
    # Create dir things that might be needed
    if not os.path.exists(message_folder):
        os.mkdir(message_folder)
    if not os.path.exists(message_folder + '/' + ip_str):
        os.mkdir(message_folder + '/' + ip_str)
    if not os.path.exists(recent_file):
        open(recent_file, 'x')


def delete_recent_posters_if_time():
    global last_clear_of_recent_posters
    if (datetime.datetime.now() - last_clear_of_recent_posters).seconds > interval_between_recent_posters_clear:
        recent_posters.clear()
        last_clear_of_recent_posters = datetime.datetime.now()


def post_new_msg(ip_str, msg):
    recent_posters.append(ip_str)
    time_str = str(round(time.time() * 1000))
    file_location = message_folder + '/' + ip_str + '/' + time_str
    recent_posts = list()
    # add to recent
    recent_posts.append(ip_str + '/' + time_str + '.txt' + os.linesep)
    with open(recent_file, 'r') as f:
        for line in f.readlines():
            if len(recent_posts) < 10:
                recent_posts.append(line)
    with open(recent_file, 'w') as f:
        for post in recent_posts:
            f.write(post)
    # write the paste
    with open(file_location, 'x') as f:
        f.write(msg)
    # While there are more than 10 files we delete the oldest
    while len(os.listdir(message_folder + '/' + ip_str)) > 10:
        oldest_file = 9999999999999999999999
        for file in os.listdir(message_folder + '/' + ip_str):
            if int(file) < oldest_file:
                oldest_file = int(file)
        os.remove(message_folder + '/' + ip_str + '/' + str(oldest_file))
    return time_str


def get_recent_post():
    recent_posts = list()
    with open(recent_file, 'r') as f:
        for post in f.readlines():
            recent_posts.append(post)
    return recent_posts


def get_your_posts(ip_str):
    ip_msg = list()
    for file in os.listdir(message_folder + '/' + ip_str):
        ip_msg.append(int(file))
    ip_msg.sort(reverse=True)
    finish_msg = list()
    for msg in ip_msg:
        finish_msg.append(ip_str + '/' + str(msg) + '.txt')
    return finish_msg


@app.route('/', methods=['POST', 'GET'])
def index():
    delete_all_msg_if_time()
    delete_recent_posters_if_time()
    ip_str = str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    ensure_dirs_exists(ip_str)

    # If you are posting to the site
    if request.method == 'POST':
        msg = request.form['msg']
        err_msg = None
        if len(msg) > max_paste_size:
            err_msg = f'paste cannot exceed {max_paste_size} bytes (yours: {len(msg)})'
        if ip_str in recent_posters:
            err_msg = f'You posted too quickly. Please wait least {interval_between_recent_posters_clear*2} seconds.'
        if err_msg:
            return render_template('single_paste.html', value=err_msg)
        return redirect('msg/' + ip_str + '/' + post_new_msg(ip_str, str(msg)) + '.txt')
    # If you are accessing the site
    if request.method == 'GET':
        recent_posts = get_recent_post()
        your_posts = get_your_posts(ip_str)
        return render_template('index.html', recent_posts=recent_posts, your_posts=your_posts)


@app.route('/msg/<ip_str>/<time_str>')
def fetch_paste(ip_str, time_str):
    msg_folder = message_folder + '/' + ip_str
    file_location = msg_folder + '/' + time_str[:-4]
    if not os.path.exists(msg_folder) or not os.path.exists(file_location):
        return redirect('/')
    with open(file_location, 'r') as f:
        return render_template('single_paste.html', value=f.read())


@app.route('/msg/<ip_str>')
def fetch_ip(ip_str):
    ip_msg = list()
    if not os.path.exists(message_folder + '/' + ip_str):
        return redirect('/')
    for file in os.listdir(message_folder + '/' + ip_str):
        ip_msg.append(ip_str + '/' + file + '.txt')
    return render_template('single_ip.html', ip_msg=ip_msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
