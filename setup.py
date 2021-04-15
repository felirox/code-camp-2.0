import os
from werkzeug.utils import secure_filename
from flask import Flask,flash,request,redirect,send_file,render_template
import pyAesCrypt
import glob
bufferSize = 64 * 1024
UPLOAD_FOLDER = 'uploads/'
# web: gunicorn setup:app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



files = glob.glob('uploads/*')
for f in files:
    os.remove(f)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about-us.html")

@app.route('/contact')
def contact():
    return render_template("contact-us.html")

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            password = request.form['query']
            filename = secure_filename(file.filename)
            file_path = UPLOAD_FOLDER + filename
            file_path_out = UPLOAD_FOLDER + filename.rsplit('.', 1)[0] +"- encrypted ." + filename.rsplit('.', 1)[1]
            filename_out = filename.rsplit('.', 1)[0] +"- encrypted ." + filename.rsplit('.', 1)[1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pyAesCrypt.encryptFile(file_path,file_path_out, password, bufferSize)
            print("saved file successfully")
      #send file name as parameter to downlad
            return redirect('/downloadfile/'+ filename_out)
    return render_template('enrypt.html')

@app.route("/downloadfile/<filename>", methods = ['GET'])
def download_file(filename):
    filename_out = filename#.rsplit('.', 1)[0] +"- encrypted ." + filename.rsplit('.', 1)[1]
    return render_template('download.html',value=filename_out)

@app.route('/return-files/<filename>')
def return_files_tut(filename):
    #file_path = UPLOAD_FOLDER + filename
    file_path_out = UPLOAD_FOLDER + filename#.rsplit('.', 1)[0] +"- encrypted ." + filename.rsplit('.', 1)[1]

    return send_file(file_path_out, as_attachment=True, attachment_filename='')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            #print("dec 1 in")
            password = request.form['query']
            filename = secure_filename(file.filename)
            file_path = UPLOAD_FOLDER + filename
            filename_first = filename.rsplit('.', 1)[0]
            filename_last = filename.rsplit('.', 1)[1]
            filename_first_split = filename_first
            filename_first_last_split = filename_first
            i=0
            while (i==0):
                #print("dec 2 while in")
                filename_first_last_split = filename_first_split[-12:]
                if (filename_first_last_split == "- encrypted " or filename_first_last_split == "-_encrypted_" ):
                    filename_first_split = filename_first_split[:-12]
                    filename_out = filename_first_split +"- decrypted ." + filename_last
                else:
                    filename_out = filename_first_split +"- decrypted ." + filename_last
                    i=1
            print("dec 3 while out")
            file_path_out = UPLOAD_FOLDER + filename_out
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                pyAesCrypt.decryptFile(file_path,file_path_out, password, bufferSize)
            except ValueError:
                return redirect('/wrongpassword')
            print("saved file decrypt successfully")
      #send file name as parameter to downlad
            return redirect('/downloadfiledec/'+ filename_out)
    return render_template("decrypt.html")

@app.route("/downloadfiledec/<filename>")
def download_file_dec(filename):
    filename_out = filename#.rsplit('.', 1)[0] +"- encrypted ." + filename.rsplit('.', 1)[1]
    return render_template('download-dec.html',value=filename_out)

@app.route("/wrongpassword")
def wrongpassword():
    return render_template('wrongpassword.html')

@app.route('/return-files-decrypt/<filename>')
def return_files_tut_dec(filename):
    #file_path = UPLOAD_FOLDER + filename
    file_path_out = UPLOAD_FOLDER + filename#.rsplit('.', 1)[0] +"- encrypted ." + filename.rsplit('.', 1)[1]

    return send_file(file_path_out, as_attachment=True, attachment_filename='')


@app.errorhandler(404)
def not_found(e):
# defining function
  return render_template("404.html")

if __name__ == '__main__':
    app.run()
