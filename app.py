from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from flask_mysqldb import MySQL
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
from LinearRegr import LinearRegressionFromScratch

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bigmart'

mysql = MySQL(app)
app.secret_key = 'SALES@123'


def validate_float(value):
    try:
        float_value = float(value)
        return float_value
    except ValueError:
        return None

def validate_input_fields(item_weight, item_fat_content, item_visibility, item_type, item_mrp, outlet_establishment_year, outlet_size, outlet_location_type, outlet_type):
    errors = []

    # Validate empty fields
    if not item_weight:
        errors.append('Item Weight is required.')
    if not item_fat_content:
        errors.append('Item Fat Content is required.')
    if not item_visibility:
        errors.append('Item Visibility is required.')
    if not item_type:
        errors.append('Item Type is required.')
    if not item_mrp:
        errors.append('Item MRP is required.')
    if not outlet_establishment_year:
        errors.append('Outlet Establishment Year is required.')
    if not outlet_size:
        errors.append('Outlet Size is required.')
    if not outlet_location_type:
        errors.append('Outlet Location Type is required.')
    if not outlet_type:
        errors.append('Outlet Type is required.')

    # Validate data types
    try:
        if item_weight:
            item_weight = float(item_weight)
        if item_fat_content:
            if item_fat_content not in ['1', '2', '0', '4', '3']:
                errors.append('Invalid Item Fat Content.')
        if item_visibility:
            item_visibility = float(item_visibility)
        if item_type:
            item_type = int(item_type)
        if item_mrp:
            item_mrp = float(item_mrp)
        if outlet_establishment_year:
            if len(outlet_establishment_year) != 4 or not outlet_establishment_year.isdigit():
                errors.append('Outlet Establishment Year must be a four-digit number.')
        if outlet_size:
            if outlet_size not in ['0', '1', '2']:
                errors.append('Invalid Outlet Size.')
        if outlet_location_type:
            if outlet_location_type not in ['0', '1', '2']:
                errors.append('Invalid Outlet Location Type.')
        if outlet_type:
            if outlet_type not in ['0', '1', '2', '3']:
                errors.append('Invalid Outlet Type.')
    except ValueError:
        errors.append('Invalid data type for one or more fields.')

    return errors



@app.route('/results', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        item_weight = request.form.get('item_weight')
        item_fat_content = request.form.get('item_fat_content')
        item_visibility = request.form.get('item_visibility')
        item_type = request.form.get('item_type')
        item_mrp = request.form.get('item_mrp')
        outlet_establishment_year = request.form.get('outlet_establishment_year')
        outlet_size = request.form.get('outlet_size')
        outlet_location_type = request.form.get('outlet_location_type')
        outlet_type = request.form.get('outlet_type')

    # Validate input fields
        errors = validate_input_fields(item_weight, item_fat_content, item_visibility, item_type, item_mrp, outlet_establishment_year, outlet_size, outlet_location_type, outlet_type)
    # # Perform validation
    # errors = []
    # if not item_weight:
    #     errors.append('Item Weight is required.')
    # if not item_fat_content:
    #     errors.append('Item Fat Content is required.')
    # if not item_visibility:
    #     errors.append('Item Visibility is required.')
    # if not item_type:
    #     errors.append('Item Type is required.')
    # if not item_mrp:
    #     errors.append('Item MRP is required.')
    # if not outlet_establishment_year:
    #     errors.append('Outlet Establishment Year is required.')
    # if not outlet_size:
    #     errors.append('Outlet Size is required.')
    # if not outlet_location_type:
    #     errors.append('Outlet Location Type is required.')
    # if not outlet_type:
    #     errors.append('Outlet Type is required.')

    # If there are errors, render the form again with error messages
    if errors:
        error_str = '&'.join([f'error={error}' for error in errors])
        return redirect(url_for('predict') + '?' + error_str)


    try:
            model_path = r'C:\Users\Predator\Desktop\Final Year PRoject\Big-Mart-Sales-Prediction-System\sc.sav'
            model = joblib.load(model_path)

            X = np.array([[item_weight, item_fat_content, item_visibility, item_type, item_mrp,
                           outlet_establishment_year, outlet_size, outlet_location_type, outlet_type]])

            Y_pred = model.predict(X.reshape(1, -1))

            return render_template('results.html', prediction=float(Y_pred))

    except Exception as e:
            return render_template('error.html', error=str(e))



@app.route("/")
def default():
    if 'email' in session:
        return render_template('home.html')
    return render_template("index.html")


@app.route("/predict")
def predict():
    if 'email' in session:
        errors = request.args.getlist('error')
        return render_template('sales_prediction.html', errors=errors)
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'email' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('Please fill in all the fields.', 'danger')
            return redirect(url_for('register'))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! Please log in.', 'success')

        return redirect(url_for('default'))

    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['email'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/home")
def home():
    if 'email' in session:
        return render_template('home.html')
    return redirect(url_for('login'))


@app.route("/about")
def about():
    if 'email' in session:
        return render_template('components/auth_about.html')
    return render_template("about.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('Please fill in all the fields.', 'danger')
            return redirect(url_for('contact'))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contact (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
        mysql.connection.commit()
        cur.close()

        flash('Your message has been sent successfully!', 'success')

        return redirect(url_for('contact'))

    if 'email' in session:
        return render_template('components/auth_contact.html')
    return render_template('contact.html')


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
