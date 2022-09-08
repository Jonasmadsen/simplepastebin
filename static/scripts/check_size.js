function check() {
    if (document.getElementById('paste_id').value.length > 512) {
        document.getElementById('message').style.color = 'red';
        document.getElementById('message').innerHTML = '512 bytes is maximum size';
    } else {
        document.getElementById('message').innerHTML = '';
    }
}