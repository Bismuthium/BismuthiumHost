from flask import Flask, send_from_directory, request, redirect, make_response, render_template_string
from better_profanity import profanity
import json
import base64
from requests import get
# change this to whatever your domain is
authuri = 'https://bismuthiumhost.glitch.me/authenticate'

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
    website_code = profanity.censor(request.form['WebCode'])
    
    # Extract IP address from the request data
    ip_address = request.form.get('ipAddress')
    
    if ip_address:
        log_message = f"{ip_address} has uploaded {website_name}"
        with open('templates/log/iplog.txt', 'a') as log_file:
            log_file.write(log_message + '\n')
    else:
        print("Unable to fetch IP address from the HTML form")
    
    save_file('templates/sites/' + website_name + '.html', website_code)
    
    return "Website hosted successfully! View it <a href='/sites/" + website_name + ".html'>here.</a>"

@app.before_request
def check_banned_ip():
    # Check if requesting IP is in the list of banned IPs
    requesting_ip = request.remote_addr
    if requesting_ip in banned_ips:
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)

"""
Credit to https://github.com/NotFenixio/ScratchAuthDemo/blob/main/api/index.py, modifed to be simplier to use in our app
"""

@app.route("/auth")
def auth():
    username = request.cookies.get("username")
    if not username:
        redirect_uri = f"https://auth.itinerary.eu.org/auth/?redirect={ base64.b64encode(authuri.encode('utf-8')).decode('utf-8') }&name=BismuthiumHost"
        return redirect(redirect_uri)
    else:
        with open('templates/auth.html', 'r') as file:
            template_string = file.read()
        rendered_template = render_template_string(template_string, username=username)
        return rendered_template

@app.route("/authenticate")
def authenticate():
    code = request.args.get("privateCode")
    
    if code is None:
        return "Bad Request", 400

    response = get(f"https://auth.itinerary.eu.org/api/auth/verifyToken?privateCode={code}").json()
    if response["redirect"] == authuri:
        if response["valid"]:
            username = response["username"]
            response = make_response(redirect("/auth"))
            response.set_cookie("username", username)
            return response
        else:
            return "Authentication failed!"
    else:
        return "Invalid Redirect", 400

if __name__ == '__main__':
    profanity.load_censor_words()
    app.run()
