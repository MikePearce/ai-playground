from flask import Flask, render_template, request, redirect, url_for, flash
import config, aicontent, os
from werkzeug.utils import secure_filename

def page_not_found(e):
  return render_template('404.html'), 404


app = Flask(__name__)
app.config.from_object(config.config['development'])
app.register_error_handler(404, page_not_found)


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html', **locals())

@app.route('/whisper', methods=["GET", "POST"])
def whisper():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'uploaded_file' not in request.files:
            flash('No file selected!')
            return redirect(request.url)
        file = request.files['uploaded_file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(config.UPLOAD_FOLDER, filename))

            openAIAnswer = aicontent.whisperQuery(os.path.join(config.UPLOAD_FOLDER, filename))
            with open('output.txt', 'w') as f:
                f.write(openAIAnswer.text)
        
    return render_template('whisper.html', **locals())


@app.route('/lesson-plan', methods=["GET", "POST"])
def productDescription():

    # define subjects
    subjects = ['Geography', 'Maths', 'History', 'Chemistry']
    grades = ['GCSE', 'A-Level', 'Key Stage 1', 'Key Stage 2']

    if request.method == 'POST':
        grade = request.form['grade']
        subject = request.form['subject']
        topic = request.form['topic']
        prompt = f'Act as a {grade} teacher in the united kingdom. Please provide me a lesson plan for a 45 minute online {subject} lesson on the subject of {topic}'
        prompt = f'Act as a {grade} one to one tutor with one student in the united kingdom. Please provide me a lesson plan for a 45 minute online {subject} lesson on the subject of {topic}'

        openAIAnswer = aicontent.openAIQuery(prompt)

    return render_template('/lesson-plan.html', **locals())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
