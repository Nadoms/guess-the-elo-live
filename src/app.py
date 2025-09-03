from flask import Flask, render_template_string
import json
from pathlib import Path

app = Flask(__name__)
SCORE_PATH = Path(__file__).parent / "score.json"

HTML = '''
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
    <h2 style="text-align:center;">Leaderboard</h2>
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

@app.route("/")
def leaderboard():
    try:
        with open(SCORE_PATH) as f:
            scores = json.load(f)
    except Exception as e:
        print(e)
        scores = {}
    leaderboard = list(scores.items())[:10]
    others = list(scores.items())[10:]
    return render_template_string(HTML, leaderboard=leaderboard, others=others)

if __name__ == "__main__":
    app.run(debug=True)
