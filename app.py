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


@app.route('/', methods=['POST', 'GET'])
def index():
    ip_str = str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr)).replace('.', '')
    if not os.path.exists(message_folder):
        os.mkdir(message_folder)
    if not os.path.exists(message_folder + '/' + ip_str):
        os.mkdir(message_folder + '/' + ip_str)
    if request.method == 'POST':
        msg = request.form['msg']
        if len(msg) > max_paste_size:
            return f'paste cannot exceed {max_paste_size} bytes'
        if (datetime.datetime.now() - last_clear).seconds > 100:
            recent_posters.clear()
        if ip_str in recent_posters:
            return f'You posted less than 2 minutes ago. Please wait a little.'
        recent_posters.append(ip_str)
        time_str = str(round(time.time() * 1000))
        file_location = message_folder + '/' + ip_str + '/' + time_str
        with open(file_location, 'x') as f:
            f.write(str(request.form['msg']))
        while len(os.listdir(message_folder + '/' + ip_str)) > 10:
            oldest_file = 9999999999999999999999
            for file in os.listdir(message_folder + '/' + ip_str):
                if int(file) < oldest_file:
                    oldest_file = int(file)
            os.remove(message_folder + '/' + ip_str + '/' + str(oldest_file))
        live_queue.append(ip_str + '/' + time_str + '.txt')
        if len(live_queue) > 10:
            live_queue.pop(0)
        return redirect('msg/' + ip_str + '/' + time_str + '.txt')
    if request.method == 'GET':
        ip_msg = list()
        for file in os.listdir(message_folder + '/' + ip_str):
            ip_msg.append(ip_str + '/' + file + '.txt')
        return render_template('index.html', live_queue=live_queue, ip_list=ip_msg)


@app.route('/msg/<ip_str>/<time_str>')
def fetch_paste(ip_str, time_str):
    msg_folder = message_folder + '/' + ip_str
    file_location = msg_folder + '/' + time_str[:-4]
    if not os.path.exists(msg_folder) or not os.path.exists(file_location):
        return render_template('index.html', live_queue=live_queue)
    with open(file_location, 'r') as f:
        return render_template('single_paste.html', value=f.read())


@app.route('/msg/<ip_str>')
def fetch_ip(ip_str):
    ip_msg = list()
    if not os.path.exists(message_folder + '/' + ip_str):
        return index()
    for file in os.listdir(message_folder + '/' + ip_str):
        ip_msg.append(ip_str + '/' + file + '.txt')
    return render_template('single_ip.html', ip_msg=ip_msg)


if __name__ == '__main__':
    app.run(debug=True)
