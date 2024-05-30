from flask import Flask, render_template, request, send_file
import result_analyser

app = Flask(__name__)

UPLOAD_FOLDER = '/uploads'
COMBINED_DATA_PATH = 'combined_data.csv'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        branch_code = request.form['branch_code']
        print(branch_code)
        file = request.files['file']
        if file:
            file_path = UPLOAD_FOLDER + '/' + file.filename
            file.save(file_path)
            result_analyser.process_csv(file_path, branch_code)

            return send_file(COMBINED_DATA_PATH, as_attachment=True, download_name="combined_data.csv")

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
