from flask import Flask, send_from_directory, request, redirect
from better_profanity import profanity
import json
import requests

app = Flask(__name__)

with open('templates/bannedip.json', 'r') as banned_ip_file:
    banned_ips = json.load(banned_ip_file)

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            return response.json().get('ip')
    except Exception as e:
        print(f"Error fetching public IP: {e}")
    return None

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
    website_code = profanity.censor(request.form['WebCode'])
    
    # Get public IP address
    ip_address = get_public_ip()
    if ip_address:
        log_message = f"{ip_address} has uploaded {website_name}"
        with open('templates/log/iplog.txt', 'a') as log_file:
            log_file.write(log_message + '\n')
    else:
        print("Unable to fetch public IP address")
    
    save_file('templates/sites/' + website_name + '.html', website_code)
    
    return "Website hosted successfully! View it <a href='/sites/" + website_name + ".html'>here.</a>"

@app.before_request
def check_banned_ip():
    # Check if requesting IP is in the list of banned IPs
    requesting_ip = get_public_ip()
    if requesting_ip in banned_ips:
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)

if __name__ == '__main__':
    profanity.load_censor_words()
    app.run()
