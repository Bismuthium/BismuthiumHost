from flask import Flask, send_from_directory, request, redirect
from better_profanity import profanity
import json
MAX_CODE_SIZE = 5 * 1024 * 1024  # 5MB

app = Flask(__name__)

with open('templates/bannedip.json', 'r') as banned_ip_file:
    banned_ips = json.load(banned_ip_file)

@app.route('/<path:filename>')
def static_file(filename):
    return send_from_directory('templates', filename)

@app.route('/')
def home():
    return send_from_directory('templates', 'index.html')

def save_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

@app.route('/host', methods=['POST'])
def host_website():
    website_name = profanity.censor(request.form['WebName'])
    uncensoredname = request.form('WebName')
    website_code = profanity.censor(request.form['WebCode'])
    
    if len(website_code) > MAX_CODE_SIZE:
        return "Error: Website code exceeds the size limit of 5MB."
    if '*' in website_name:
        return "Error: Website name cannot contain " + uncensoredname + " " + "Please choose a different name."

    # Log IP address and website name, for safety
    ip_address = request.remote_addr
    log_message = f"{ip_address} has uploaded {website_name}"
    with open('templates/log/iplog.txt', 'a') as log_file:
        log_file.write(log_message + '\n')
    
    save_file('templates/sites/' + website_name + '.html', website_code)
    
    return "Website hosted successfully! View it <a href='/sites/" + website_name + ".html'>here.</a>"

@app.before_request
def check_banned_ip():
    # Check if requesting IP is in the list of banned IPs
    requesting_ip = request.remote_addr
    if requesting_ip in banned_ips:
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)

if __name__ == '__main__':
    profanity.load_censor_words()
    app.run()
