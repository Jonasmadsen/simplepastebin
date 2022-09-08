import datetime
import os.path
import time

from flask import Flask, render_template, request, redirect

app = Flask(__name__)

live_queue = []
recent_posters = list()
max_paste_size = 512
message_folder = 'msg'
last_clear = datetime.datetime.now()
recent_file = message_folder + '/' + 'recent.txt'

@app.route('/', methods=['POST', 'GET'])
def index():
    forwarded_header = request.headers.get("X-Forwarded-For")
    if forwarded_header:
        ip_str = request.headers.getlist("X-Forwarded-For")[0].replace('.', '')
    else:
        ip_str = str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr)).replace('.', '')

    # Create dir things that might be needed
    if not os.path.exists(message_folder):
        os.mkdir(message_folder)
    if not os.path.exists(message_folder + '/' + ip_str):
        os.mkdir(message_folder + '/' + ip_str)
    if not os.path.exists(recent_file):
        open(recent_file, 'x')

    # If you are posting to the site
    if request.method == 'POST':
        msg = request.form['msg']
        if len(msg) > max_paste_size:
            return f'paste cannot exceed {max_paste_size} bytes'
        if (datetime.datetime.now() - last_clear).seconds > 1:
            recent_posters.clear()
        if ip_str in recent_posters:
            return f'You posted less than 2 minutes ago. Please wait a little.'
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
            f.write(str(request.form['msg']))
        while len(os.listdir(message_folder + '/' + ip_str)) > 10:
            oldest_file = 9999999999999999999999
            for file in os.listdir(message_folder + '/' + ip_str):
                if int(file) < oldest_file:
                    oldest_file = int(file)
            os.remove(message_folder + '/' + ip_str + '/' + str(oldest_file))
        return redirect('msg/' + ip_str + '/' + time_str + '.txt')
    if request.method == 'GET':
        recent_posts = list()
        with open(recent_file, 'r') as f:
            for post in f.readlines():
                recent_posts.append(post)
        ip_msg = list()
        for file in os.listdir(message_folder + '/' + ip_str):
            ip_msg.append(int(file))
        ip_msg.sort(reverse=True)
        finish_msg = list()
        for msg in ip_msg:
            finish_msg.append(ip_str + '/' + str(msg) + '.txt')
        return render_template('index.html', recent_posts=recent_posts, ip_list=finish_msg)


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
