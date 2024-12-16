from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token
import models

# Initialize Flask app
app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'Infosys-Springboard-5.0'  

# Initialize extensions
db = models.db
jwt = JWTManager(app)

# Initialize the SQLAlchemy instance with app (must happen after app creation)
db.init_app(app)

# Create all tables (ensure app context is available)
with app.app_context():
    db.create_all()  

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if models.User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = models.User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = models.User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid username or password'}), 401

    # Generate JWT token
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login")
def loginPage():
    return render_template('login.html')

@app.route("/signup")
def signupPage():
    return render_template('signup.html')

@app.route("/admin/api/additems", methods=['POST'])
def addItems():
    data = request.get_json()

    # Validate input data
    name = data.get('name')
    price = data.get('price')
    category = data.get('category')
    brand = data.get('brand')
    image = data.get('image')

    if not all([name, price, category, brand]):
        return jsonify({'message': 'All fields except image are required'}), 400

    try:
        # Create new product
        new_product = models.Product(
            name=name,
            price=float(price),
            category=category,
            brand=brand,
            image=image  
        )

        # Add to database
        db.session.add(new_product)
        db.session.commit()

        return jsonify({'message': 'Product added successfully'}), 201
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(debug=True)