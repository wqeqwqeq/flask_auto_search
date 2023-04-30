import os
from flask import (
    Flask,
    request,
    render_template,
    flash,
    redirect,
    url_for,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from backend import process_link as pl
from backend import process_word as pw

UPLOAD_FOLDER = "./test"
ALLOWED_EXTENSIONS = {"txt"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        print(request.files, request.form)
        wordtxt = request.files["wordtxt"]
        linktxt = request.files["linktxt"]
        case = True if request.form["case"] == "True" else False
        exact = True if request.form["exact"] == "True" else False
        above = int(request.form["above"])
        below = int(request.form["below"])
        deep_dive = True if request.form["deep_dive"] == "True" else False
        level = int(request.form["level"])
        stimeout = int(request.form["stimeout"])

        if wordtxt.filename == "" or linktxt.filename == "":
            flash("Please upload both word.txt and link.txt")
            return redirect(request.url)

        if wordtxt and allowed_file(wordtxt.filename):
            filename = secure_filename(wordtxt.filename)
            wordtxt.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            word = pw.get_word_from_path(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

        if linktxt and allowed_file(linktxt.filename):
            filename = secure_filename(linktxt.filename)
            linktxt.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            link = pl.get_link_from_path(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

        file_lk_map, fail_lst = pl.write_to_files(
            link, deep_dive=False, level=level, timeout=stimeout
        )
        print("finish parse")
        pw.run_search(
            file_lk_map,
            word,
            above=above,
            below=below,
            ignore_case=case,
            exact_match=exact,
        )
        filename = "result.xlsx"
        finish = True
        return render_template("upload.html", finish=finish, filename=filename)
    return render_template("upload.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("./result", filename)


if __name__ == "__main__":
    app.run(debug=True)
