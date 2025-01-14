from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# MySQL database connection configuration
db_config = {
    "host": "mysql-container",
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

@app.route('/employees', methods=['GET'])
def get_employees():
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
def add_employees():
    data = request.json  # Expecting an array of employee data
    if not isinstance(data, list):
        return jsonify({"error": "Request body should be an array of employee objects"}), 400

    try:
        # Connect to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # Insert query
        query = """
        INSERT INTO employees (name, position, salary, grade, EMAIL)
        VALUES (%s, %s, %s, %s, %s)
        """

        # Prepare and execute queries for multiple rows
        values = [(employee['name'], employee['position'], employee['salary'], employee['grade'], employee['EMAIL']) for employee in data]
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
def update_employee(employee_id):
    try:
        data = request.get_json()
        connection = get_db_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = connection.cursor()
        query = "UPDATE employees SET name=%s, position=%s, salary=%s, grade=%s, EMAIL=%s WHERE id=%s"
        values = (data['name'], data['position'], data['salary'], data['grade'], data['EMAIL'], employee_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Employee updated successfully"})
    except Exception as e:
        logger.error(f"Error updating employee: {e}")
        return jsonify({"error": str(e)}), 500

