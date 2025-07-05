from flask import Flask, request, redirect, render_template_string
from datetime import datetime, timedelta
import csv
import os

app = Flask(__name__)
DATA_FILE = "data.csv"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Tesla Tracker</title>
</head>
<body>
    <h1>🚗 Tesla Tracker</h1>
    <form method="post" action="/submit">
        Name:
        <select name="name" required>
            <option value="Bulent Kiser">Bulent Kiser</option>
            <option value="Ozan Kiser">Ozan Kiser</option>
        </select><br>

        Earnings ($): <input type="number" name="earnings" step="0.01" required><br>
        Charge Cost ($): <input type="number" name="charge" step="0.01" required><br>
        <button type="submit">Submit</button>
    </form>

    <hr>

    <h2>📊 Records</h2>
    <table border="1">
        <tr>
            <th>Date</th>
            <th>Name</th>
            <th>Earnings</th>
            <th>Charge</th>
            <th>Net</th>
            <th>Edit</th>
        </tr>
        {% for row in records %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>${{ row[2] }}</td>
            <td>${{ row[3] }}</td>
            <td>${{ ("%.2f"|format(row[2]|float - row[3]|float)) }}</td>
            <td><a href="/edit/{{ loop.index0 }}">✏️</a></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def get_today_date_adjusted():
    now = datetime.now()
    if now.hour < 4:
        now -= timedelta(days=1)
    return now.strftime("%m%d%y")

@app.route("/")
def index():
    records = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline='') as f:
            reader = csv.reader(f)
            records = list(reader)
    return render_template_string(HTML, records=records)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    earnings = request.form["earnings"]
    charge = request.form["charge"]
    date = get_today_date_adjusted()

    with open(DATA_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date, name, earnings, charge])
    return redirect("/")

@app.route("/edit/<int:row_id>", methods=["GET", "POST"])
def edit(row_id):
    records = []
    with open(DATA_FILE, newline='') as f:
        reader = csv.reader(f)
        records = list(reader)

    if request.method == "POST":
        new_earnings = request.form["earnings"]
        new_charge = request.form["charge"]

        records[row_id][2] = new_earnings
        records[row_id][3] = new_charge

        with open(DATA_FILE, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(records)

        return redirect("/")

    selected = records[row_id]
    return f"""
    <h2>Edit Entry</h2>
    <form method="post">
        Name: <strong>{selected[1]}</strong><br>
        Earnings ($): <input type="number" name="earnings" step="0.01" value="{selected[2]}" required><br>
        Charge ($): <input type="number" name="charge" step="0.01" value="{selected[3]}" required><br>
        <button type="submit">Save</button>
    </form>
    <br>
    <a href="/">⬅️ Back</a>
    """

if __name__ == "__main__":
    app.run(debug=True, port=5001)
