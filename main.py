from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
import requests


app = Flask(__name__)
app.config["SECRET_KEY"] = "sakfjlaksfjlaskfjalss/a,fasjf"
bootstrap = Bootstrap5
bootstrap(app)

response = requests.get(url="https://opentdb.com/api_category.php")
categories = response.json()["trivia_categories"]

list_categories = [category for category in categories]


@app.route("/")
def home():
    return render_template("index.html", list_categories=list_categories)


@app.route("/select-difficulty")
def select_difficulty():
    if request.args.get("empty"):
        empty = True
        difficulty = request.args.get("difficulty")
    else:
        empty = False
        difficulty = None
    category_id = request.args.get("id")
    list_difficulties = ["Easy", "Medium", "Hard"]
    return render_template(
        "select-difficulty.html",
        category_id=category_id,
        list_difficulties=list_difficulties,
        empty=empty,
        difficulty=difficulty,
    )


@app.route("/take-quiz")
def take_quiz():
    category_id = request.args.get("id")
    difficulty = request.args.get("difficulty").lower()
    params = {"category": category_id, "type": "multiple", "difficulty": difficulty}
    response = requests.get(url=f"https://opentdb.com/api.php?amount=10", params=params)
    questions = response.json()["results"]
    if questions == []:
        return redirect(
            url_for(
                "select_difficulty",
                id=category_id,
                empty=True,
                difficulty=difficulty,
            )
        )
    return render_template("take-quiz.html", questions=questions, num_q=len(questions))


if __name__ == "__main__":
    app.run(debug=True)
