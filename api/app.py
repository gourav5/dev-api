from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import mysql.connector
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# JWT configuration
app.config["JWT_SECRET_KEY"] = "f3b9c1e80a6ef2d9f1c95d1ef45e3a0d939c712ad5c2d273dd68c4e0c9e0d8f2"  # Replace with a secure secret key
jwt = JWTManager(app)

# MySQL database connection configuration
db_config = {
    "host": "mysql",
    "user": "testuser",
    "password": "testpassword",
    "database": "testdb"
}

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/logs/api.log"),  # Write logs to a file inside the container
        logging.StreamHandler()  # Output logs to console for real-time monitoring
    ]
)

logger = logging.getLogger(__name__)

# Test database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Exception as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None


@app.route('/login', methods=['POST'])
def login():
    """Endpoint to authenticate users and provide a token"""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Verify the username and password (this should ideally be done via a database query)
    if username == "admin" and password == "admin":  # Replace with real authentication logic
        access_token = create_access_token(identity={"username": username})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@app.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """Endpoint to fetch all employees (requires a valid token)"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees")
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/employees', methods=['POST'])
@jwt_required()
def add_employees():
    """Endpoint to add new employees (requires a valid token)"""
    data = request.json  # Expecting an array of employee data
    if not isinstance(data, list):
        return jsonify({"error": "Request body should be an array of employee objects"}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # Insert query
        query = """
        INSERT INTO employees (name, position, salary)
        VALUES (%s, %s, %s)
        """

        # Prepare and execute queries for multiple rows
        values = [(employee['name'], employee['position'], employee['salary']) for employee in data]
        cursor.executemany(query, values)
        conn.commit()

        return jsonify({"message": f"{cursor.rowcount} employees added successfully"}), 201

    except Exception as e:
        logger.error(f"Error adding employees: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/employees/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """Endpoint to update an employee (requires a valid token)"""
    try:
        data = request.get_json()
        connection = get_db_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = connection.cursor()
        query = "UPDATE employees SET name=%s, position=%s, salary=%s WHERE id=%s"
        values = (data['name'], data['position'], data['salary'], employee_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Employee updated successfully"})
    except Exception as e:
        logger.error(f"Error updating employee: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)

