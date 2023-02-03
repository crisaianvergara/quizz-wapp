from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
import requests
import random
import os


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
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
    category_id = request.args.get("id")
    if request.args.get("empty"):
        empty = True
        difficulty = request.args.get("difficulty")
    elif request.args.get("game_on"):
        difficulty = request.args.get("difficulty").lower()
        params = {"category": category_id, "type": "multiple", "difficulty": difficulty}
        response = requests.get(
            url="https://opentdb.com/api.php?amount=10", params=params
        )
        global questions
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
        return redirect(url_for("take_quiz", num_q=0))
    else:
        empty = False
        difficulty = None
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
    num_q = int(request.args.get("num_q"))
    if (
        num_q == 0
        and not request.args.get("check_on")
        and not request.args.get("quiz_on")
    ):
        question = questions[num_q]
        score = 0
        return render_template(
            "take-quiz.html", question=question, num_q=0, track=num_q + 1, score=score
        )
    elif request.args.get("check_on"):
        num_q = int(request.args.get("num_q"))
        if len(questions) > num_q:
            question = questions[num_q]
            is_correct = request.args.get("is_correct")
            if is_correct == "True":
                score = int(request.args.get("score")) + 1
            else:
                score = int(request.args.get("score"))
            return render_template(
                "take-quiz.html",
                question=question,
                num_q=num_q,
                is_correct=is_correct,
                track=num_q + 1,
                score=score,
            )
    elif request.args.get("quiz_on") and not request.args.get("check_on"):
        num_q = int(request.args.get("num_q"))
        if len(questions) - 1 > num_q:
            num_q += 1
            question = questions[num_q]
            score = int(request.args.get("score"))
            return render_template(
                "take-quiz.html",
                question=question,
                num_q=num_q,
                track=num_q + 1,
                score=score,
            )
        return "finish"


@app.route("/check-answer", methods=["GET", "POST"])
def check_answer():
    if request.method == "POST":
        data = request.form
        score = data["score"]
        if data["correct_answer"] == data["answer"]:
            return redirect(
                url_for(
                    "take_quiz",
                    is_correct=True,
                    num_q=data["num_q"],
                    check_on=True,
                    score=score,
                )
            )
        return redirect(
            url_for(
                "take_quiz",
                is_correct=False,
                num_q=data["num_q"],
                check_on=True,
                score=score,
            )
        )


if __name__ == "__main__":
    app.run(debug=True)
