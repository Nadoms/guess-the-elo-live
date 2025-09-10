from flask import Flask, render_template_string
import json
from pathlib import Path

app = Flask(__name__)
ROOT = Path(__file__).parent

LB_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Leaderboard</title>
    <meta http-equiv="refresh" content="2">
    <style>
        body { font-family: Minecraft; font-size: 2em; background: #222; color: #eee; }
        table { border-collapse: collapse; }
        th, td { border: 1px solid #444; padding: 8px; text-align: center; }
        th { background: #333; color: #ffff55; }
        tr:nth-child(even) { background: #282828; }
        tr:nth-child(odd) { background: #1a1a1a; }
        h2 { font-size: 3em; color: #ffff55; margin-top: 0.5em; }
    </style>
</head>
<body>
    <h2 style="text-align:center;">Chat Leaderboard</h2>
    <div style="display: flex; justify-content: center; align-items: flex-start; gap: 3em;">
        <table>
            <tr>
                <th>Rank</th>
                <th>Name</th>
                <th>Score</th>
                <th>Last Guess</th>
            </tr>
            {% for username, data in leaderboard %}
            <tr>
                <td>#{{ loop.index }}</td>
                <td>{{ username }}</td>
                <td>{{ data['score'] }}</td>
                <td>{{ data['guess'] }}</td>
            </tr>
            {% endfor %}
        </table>
        {% if others %}
            <table style="width: 250px; font-size: 0.5em;">
                {% for username, data in others %}
                <tr style="height: 32px;">
                    <td>#{{ loop.index + 10 }}</td>
                    <td>{{ username }}</td>
                    <td>{{ data['score'] }}</td>
                    <td>{{ data['guess'] }}</td>
                </tr>
                {% endfor %}
            </table>
        {% endif %}
    </div>
</body>
</html>
'''

FEED_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Live Guesses</title>
    <meta http-equiv="refresh" content="2">
    <style>
        body { font-family: Minecraft; font-size: 2em; background: #222; color: #eee; }
        table { border-collapse: collapse; margin: 2em auto; width: 60%; }
        th, td { border: 1px solid #444; padding: 8px; text-align: center; }
        th { background: #333; color: #ffff55; }
        tr:nth-child(even) { background: #282828; }
        tr:nth-child(odd) { background: #1a1a1a; }
        h2 { font-size: 3em; color: #ffff55; margin-top: 0.5em; }
    </style>
</head>
<body>
    <h2 style="text-align:center;">Live Guesses</h2>
    <table>
        <tr>
            <th>Username</th>
            <th>Guess</th>
        </tr>
        {% for username, guess in feed %}
        <tr>
            <td>{{ username }}</td>
            <td>{{ guess }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

@app.route("/lb")
def leaderboard():
    try:
        with open(ROOT / "score.json") as f:
            scores = json.load(f)
    except Exception as e:
        print(e)
        scores = {}
    leaderboard = list(scores.items())[:10]
    others = list(scores.items())[10:]
    return render_template_string(LB_HTML, leaderboard=leaderboard, others=others)

@app.route("/feed")
def feed():
    try:
        with open(ROOT / "feed.json") as f:
            feed = reversed(json.load(f)[-10:])
    except Exception as e:
        print(e)
        feed = []
    return render_template_string(FEED_HTML, feed=feed)

SCORE_PATH = Path(__file__).parent / "score.json"

if __name__ == "__main__":
    app.run(debug=True)
