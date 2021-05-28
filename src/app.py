from flask import Flask, jsonify, request

from mysql.connector import connect, Error

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello!"

@app.route('/user/create/')
def create_user():
    firstname = request.args.get("firstname")
    lastname = request.args.get("lastname")
    email = request.args.get("email")

    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (firstname, lastname, email) VALUES ('{0}', '{1}', '{2}')".format(firstname, lastname, email))
        connection.commit()
    except Error as e:
        print(e)
        return "Error", 500
    finally:
        connection.close()
        return "ok"

@app.route('/user/view/<id>')
def view_user(id):
    sort = request.args.get("sort") #firstname, lastname

    if sort == None:
        sort = "NULL"

    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM `users` WHERE `id` = '{0}' ORDER BY {1}".format(id, sort))
        result = cursor.fetchall()
    except Error as e:
        print(e)
        return "Error", 500
    finally:
        connection.close()
        return jsonify(result)


@app.route('/user/edit/<id>')
def edit_user(id):
    firstname = request.args.get("firstname")
    lastname = request.args.get("lastname")
    email = request.args.get("email")

    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("UPDATE `users` SET firstname=`{0}`,lastname=`{1}`,email=`{2}`".format(firstname, lastname, email))
        connection.commit()
    except Error as e:
        print(e)
        return "error", 500
    finally:
        connection.close()
    return "ok"

@app.route('/user/delete/<id>')
def delete_user(id):
    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM `users` WHERE `id`=`{0}`".format(id))
    except Error as e:
        print(e)
        return "Error", 500
    finally:
        connection.close()
        return "ok"

@app.route('/transaction/create/')
def create_transaction():
    user_id = request.args.get("user_id")
    amount = request.args.get("amount")
    date = request.args.get("date")

    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO transactions (user_id, amount, date) VALUES ('{0}', '{1}', '{2}')".format(user_id, amount, date))
        connection.commit()
    except Error as e:
        print(e)
        return "Error", 500
    finally:
        connection.close()
        return "ok"

@app.route('/transaction/view/<id>')
def view_transaction(id):
    sort = request.args.get("sort") #date, amount
    type = request.args.get("type")
    date = request.args.get("date")

    if sort == None:
        sort = "NULL"

    #might look like some black magic
    #Depending on client input, generating substring to insert to sql query
    if type == "income":
        type = "and `amount` > '0'"
    elif type == "outcome":
        type = "and `amount` < '0'"
    else:
        type = ""

    if date==None:
        date = ""

    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM `transactions` WHERE `id` = '{0}' {1} {2} ORDER BY {3}".format(id, type, date, sort))
        result = cursor.fetchall()
    except Error as e:
        print(e)
        return "Error", 500
    finally:
        connection.close()
        return jsonify(result)

@app.route('/transaction/edit/<id>')
def edit_transaction(id):
    user_id = request.args.get("user_id")
    amount = request.args.get("amount")
    date = request.args.get("date")

    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE `transactions` SET user_id=`{0}`,amount=`{1}`,date=`{2}`".format(user_id, amount, date))
        connection.commit()
    except Error as e:
        print(e)
        return "error", 500
    finally:
        connection.close()
    return "ok"

@app.route('/transaction/delete/<id>')
def delete_transaction(id):
    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM `transactions` WHERE `id`=`{0}`".format(id))
    except Error as e:
        print(e)
        return "Error", 500
    finally:
        connection.close()
        return "ok"

@app.route('/user/payments/<id>')
def user_payments(id):
    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM `transactions` WHERE `user_id`=`{0}`".format(id))
        result = cursor.fetchall()
    except Error as e:
        print(e)
        return "Error", 500
    finally:
        connection.close()
        return jsonify(result)

@app.route('/user/income/<id>')
def user_income(id):
    start = request.args.get("start")
    end = request.args.get("end")
    day = request.args.get("date")

    if day == None and (start == None or end == None):
        return "Wrong params"

    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()

        if day != None: #if day param exists, than search transactions only for one day
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE `date`='{0}' and `amount` > '0'".format(day))
        else: #else means, that client wants to get income on range
            cursor.execute("SELECT SUM(amount) FROM tarnsactions WHERE (`date` between '{0}' and '{1}') and (`amount` > '0')".format(start, end))

        result = cursor.fetchone()[0]
        print(result)
    except Error as e:
        print(e)
        return "Error", 500
    finally:
        connection.close()
        if day != None:
            return jsonify({'income': str(result), 'date': day})
        else:
            return jsonify({'income': str(result), 'start': start, 'end': end})

@app.route('/user/outcome/<id>')
def user_outcome(id):
    start = request.args.get("start")
    end = request.args.get("end")
    day = request.args.get("date")

    if day == None and (start == None or end == None):
        return "Wrong params"

    try:
        connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
        cursor = connection.cursor()

        if day != None: #if day param exists, than search transactions only for one day
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE `date`='{0}' and `amount` <= '0'".format(day))
        else: #else means, that client wants to get income on range
            cursor.execute("SELECT SUM(amount) FROM tarnsactions WHERE (`date` between '{0}' and '{1}') and (`amount` <= '0')".format(start, end))

        result = cursor.fetchone()[0]
        print(result)
    except Error as e:
        print(e)
        return "Error", 500
    finally:
        connection.close()
        if day != None:
            return jsonify({'outcome': str(result), 'date': day})
        else:
            return jsonify({'outcome': str(result), 'start': start, 'end': end})


if __name__ == '__main__':
    app.run(host="0.0.0.0")


def get_connection(host, user, password, db):
    return connect(
        host=host,
        user=user,
        password=password,
        database=db
    )

# init MySQL Tables, creates tables
def init_database():
    connection = get_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
    cursor = connection.cursor()
    try:
        # init Users table
        cursor.execute(initUsersTable)
        connection.commit()
    except Error as e:
        print(e)  # continue if already exists

    try:
        # init Transactions table
        cursor.execute(initTransactionsTable)
        connection.commit()
    except Error as e:  # continue if already exists
        print(e)
    connection.close()


DB_HOST = 'db'
DB_USER = 'root'
DB_PASSWORD = 'examplePassword'
DB_DATABASE = 'main'


initUsersTable = """
    CREATE TABLE `users` ( 
        `id` int NOT NULL AUTO_INCREMENT, 
        `firstname` varchar(20) CHARACTER SET armscii8 COLLATE armscii8_general_ci NOT NULL,
        `lastname` varchar(20) CHARACTER SET armscii8 COLLATE armscii8_general_ci NOT NULL,
        `email` varchar(30) CHARACTER SET armscii8 COLLATE armscii8_general_ci NOT NULL,
        PRIMARY KEY (`id`)
    )
"""

initTransactionsTable = """
    CREATE TABLE `transactions` (
      `id` int NOT NULL AUTO_INCREMENT,
      `user_id` int NOT NULL,
      `amount` int NOT NULL,
      `date` date NOT NULL,
      PRIMARY KEY (`id`)
    )
"""