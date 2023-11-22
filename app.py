from flask import Flask, render_template, request, redirect, url_for, session, g
import mysql.connector

app = Flask(__name__)
app.secret_key = "vlanz"

# Configuration options for the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="vlanz"
)

# Using a cursor to perform SQL queries
cursor = db.cursor()

# Route to show the main home screen which asks the user to log in or register
@app.route('/')
def index():
    return render_template('index.html')

# Route to register a user as a customer/freelancer
@app.route('/register', methods=['GET', 'POST'])
def register():        
    try:
        if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                user_type = request.form['user_type']
                LName = request.form['LName']
                FName = request.form['FName']
                PhoneNo = request.form['PhoneNo']
                Location = request.form['Location']

                if user_type == 'customer':
                    # Insert customer data into the 'customer' table                
                    cursor.execute("INSERT INTO customer (username, password, LName, FName, PhoneNo, Location) VALUES (%s, %s, %s, %s, %s, %s)", (username, password, LName, FName, PhoneNo, Location))
                elif user_type == 'freelancer':
                    # Insert freelancer data into the 'freelancer' table
                    cursor.execute("INSERT INTO freelancer (username, password, LName, FName, PhoneNo, Location) VALUES (%s, %s, %s, %s, %s, %s)", (username, password, LName, FName, PhoneNo, Location))
                db.commit()
                return redirect(url_for('login'))
    
    except Exception as e:
        return str(e)

    return render_template('register.html')

# Route to login as a customer/freelancer
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Check if the user is a customer
            cursor.execute("SELECT * FROM customer WHERE username = %s AND password = %s", (username, password))
            customer = cursor.fetchone()

            if customer:
                cursor.fetchall()

                # Set session variables for the logged-in customer
                session['user_id'] = customer[0]
                session['user_type'] = 'customer'
                return redirect(url_for('customer_home', customer_id=customer[0]))

            # Check if the user is a freelancer
            cursor.execute("SELECT * FROM freelancer WHERE username = %s AND password = %s", (username, password))
            freelancer = cursor.fetchone()

            if freelancer:
                cursor.fetchall()

                # Set session variables for the logged-in freelancer
                session['user_id'] = freelancer[0]
                session['user_type'] = 'freelancer'
                return redirect(url_for('freelancer_home', freelancer_id=freelancer[0]))
            
    except Exception as e:
        return str(e)

    return render_template('login.html')

# Route to display the home page as a freelancer
@app.route('/freelancer_home/<int:freelancer_id>', methods=['GET', 'POST'])
def freelancer_home(freelancer_id):
    try:
        g.freelancer_id = freelancer_id

        # Function to get the name of the freelancer logged in
        cursor.execute("SELECT get_freelancer_name(%s)", (freelancer_id,))
        freelancer_info = cursor.fetchone()[0]

        # Aggregated query to get the average cost of all services provided by a freelancer
        cursor.execute("SELECT ROUND(AVG(cost), 2) FROM service WHERE freelancer_id = %s AND deleted = 0", (freelancer_id,))
        average_cost = cursor.fetchone()[0]

        if request.method == 'POST':
            name = request.form['name']
            domain = request.form['domain']
            description = request.form['description']
            cost = request.form['cost']

            # Insert new service provided by the freelancer
            cursor.execute("INSERT INTO service (freelancer_id, name, domain, description, cost) VALUES (%s, %s, %s, %s, %s)", (freelancer_id, name, domain, description, cost))
            db.commit()

        # Retrieve all services provided by the freelancer
        cursor.execute("SELECT * FROM service WHERE freelancer_id = %s AND deleted = 0", (freelancer_id,))
        services = cursor.fetchall()

    except Exception as e:
        return str(e)

    return render_template('freelancer_home.html', freelancer_info=freelancer_info, freelancer_id=freelancer_id, services=services, average_cost=average_cost)

# Route to display the home page as a customer
@app.route('/customer_home/<int:customer_id>')
def customer_home(customer_id):
    try:
        g.customer_id = customer_id 

        # Function to get the name of the customer logged in
        cursor.execute("SELECT get_customer_name(%s)", (customer_id,))
        customer_info = cursor.fetchone()[0]

        # Aggregated query to count the total number of orders by a customer
        cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = %s", (customer_id,))
        total_orders = cursor.fetchone()[0]

        # Nested query to get services not ordered by the customer
        cursor.execute("SELECT * FROM service WHERE id NOT IN (SELECT service_id FROM orders WHERE customer_id = %s) AND deleted = 0", (customer_id,))
        services = cursor.fetchall()

        # Join query to get order history of the customer
        cursor.execute("SELECT s.name, s.domain, s.description, o.date_and_time, o.service_id FROM orders o JOIN service s ON o.service_id = s.id WHERE o.customer_id = %s", (customer_id,))
        order_history = cursor.fetchall()
    
    except Exception as e:
        return str(e)

    return render_template('customer_home.html', customer_info=customer_info, services=services, order_history=order_history, total_orders=total_orders)
    
# Route to add a new service by a freelancer
@app.route('/add_service/<int:freelancer_id>', methods=['GET', 'POST'])
def add_service(freelancer_id):
    try:
        if request.method == 'POST':
            name = request.form['name']
            domain = request.form['domain']
            description = request.form['description']
            cost = request.form['cost']

            # Insert new service provided by the freelancer
            cursor.execute("INSERT INTO service (freelancer_id, name, domain, description, cost) VALUES (%s, %s, %s, %s, %s)", (freelancer_id, name, domain, description, cost))
            db.commit()

            return redirect(url_for('freelancer_home', freelancer_id=freelancer_id))
    
    except Exception as e:
        return str(e)

    return render_template('add_service.html', freelancer_id=freelancer_id)

# Route to update a service provided by a freelancer
@app.route('/update_service/<int:freelancer_id>/<int:service_id>', methods=['GET', 'POST'])
def update_service(freelancer_id, service_id):
    try:
        g.freelancer_id = freelancer_id

        # Retrieve the service details for the update
        cursor.execute("SELECT * FROM service WHERE id = %s", (service_id,))
        service = cursor.fetchone()

        if request.method == 'POST':
            name = request.form['name']
            domain = request.form['domain']
            description = request.form['description']
            cost = request.form['cost']

            # Call the stored procedure to update the service
            cursor.callproc('update_service', (service_id, name, domain, description, cost))
            db.commit()

            return redirect(url_for('freelancer_home', freelancer_id=freelancer_id))
    
    except Exception as e:
        return str(e)
    
    return render_template('update_service.html', freelancer_id=freelancer_id, service=service)

# Route to delete a service provided by a freelancer
@app.route('/delete_service/<int:freelancer_id>/<int:service_id>')
def delete_service(freelancer_id, service_id):
    try:
        # Call the stored procedure to delete the service
        cursor.callproc('delete_service', (service_id,))
        db.commit()
    
    except Exception as e:
        return str(e)

    return redirect(url_for('freelancer_home', freelancer_id=freelancer_id))

# Route to buy a freelancer's service as a customer
@app.route('/buy_service/<int:customer_id>/<int:service_id>')
def buy_service(customer_id, service_id):
    try:
        # Insert a new order for the service purchased by the customer
        cursor.execute("INSERT INTO orders (customer_id, service_id) VALUES (%s, %s)", (customer_id, service_id))
        db.commit()
    
    except Exception as e:
        return str(e)

    return redirect(url_for('customer_home', customer_id=customer_id))

# Route to cancel an order of a service purchased by a customer
@app.route('/cancel_order/<int:customer_id>/<int:service_id>')
def cancel_order(customer_id, service_id):
    try:
        # Delete the order for the service canceled by the customer
        cursor.execute("DELETE FROM orders WHERE customer_id = %s AND service_id = %s", (customer_id, service_id))
        db.commit()

        return redirect(url_for('customer_home', customer_id=customer_id))

    except Exception as e:
        return str(e)

# Route for the current user to logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)