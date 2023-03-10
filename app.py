from flask import Flask, render_template, request, redirect, url_for, flash, Markup
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

@app.route('/document', methods=["GET", "POST"])
def documents():
    standards = {
        "ISO 9001" : "Quality Management", 
        "ISO 27001" : "Information Security", 
        "ISO 14001" : "Environmental Management", 
        "ISO 13485" : "Medical Devices",
        "ISO 31000" : "Risk Management",
        "ISO 19011" : "Auditing Management"
    }

    industries = [
        "Construction",
        "Education",
        "IT Security",
        "Food Preparation"
    ]
    
    if request.method == 'POST':
        post_standard = request.form["standard"]
        post_industry = request.form["industry"]
        post_orgname = request.form["orgname"]
        post_docname = request.form["docname"]

        vowels = ['a', 'e', 'i', 'o']
        letter = "an" if post_industry[0] in vowels else "a"
        letter2 = "an" if post_docname[0] in vowels else "a"

        query = f"Act as {letter} consultant for {post_standard} {post_industry} company called '{post_orgname}'. Write {letter2} {post_docname}. Include relevant section headings. Format it in HTML."
        openAIAnswerUnformatted = aicontent.openAIQuery(query)
        
        answer = openAIAnswerUnformatted.replace('\n\n', '<br />')
        answer = answer.replace('<!--', '')
        openAIAnswer = Markup(answer)

        prompt = f'{post_docname} ({post_standard})'

    return render_template('document.html', **locals())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
