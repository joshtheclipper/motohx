from flask import Flask, redirect, render_template, request

app = Flask(__name__)

maintenance_records = []


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        new_date = request.form.get("date")
        new_service = request.form.get("service")
        new_mileage = request.form.get("mileage")

        new_record = {"date": new_date, "service": new_service, "mileage": new_mileage}

        maintenance_records.append(new_record)

        return redirect("/")

    return render_template("index.html", logs=maintenance_records)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
