from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import requests
import json
import ast
import re
import sys


app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route("/",  methods = ['GET', 'POST'])
def index():
    reload(sys)
    sys.setdefaultencoding("utf-8")
    if request.method == 'POST':
        if request.form['Search'] == 'Search':
            #url = "http://teamveracity.web.engr.illinois.edu/journals.php"
            query = request.form["query"]
            numResults = request.form["numResults"]
            url = 'http://teamveracity.web.engr.illinois.edu/journals.php?search=' + str(query) + '&max=' + str(numResults)
            data = {'searchQuery': request.form['query'], 'numResults': request.form['numResults']}
            r = requests.post(url, data)
            data = json.loads(r.text)
            #data = (r.text).decode('utf-8','ignore')
            #data = json.loads(unicode(r.text, "ISO-8859-1"))
            for paper in data:
                for i in ['title', 'authors', 'journal', 'publication_year', 'veracity']:
                    try:
                        if paper[i] == None or paper[i] == "null" or paper[i] == u"\u0000" or paper[i] == "[]":
                            paper[i] = '-'

                        elif i == 'authors':
                            final_auth_str = ''
                            a = ast.literal_eval(paper[i])
                            for auth in a:
                                auth = auth.encode('utf-8')
                                final_auth_str = final_auth_str + str(auth) + ", "
                            final_auth_str = final_auth_str[:-2]
                            paper[i] = final_auth_str


                    except:
                        pass


            return render_template('index.html', data=data)

    return render_template('index.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect(url_for('uploaded_file',
                                filename=filename))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == "__main__":
    app.run(debug=True)
