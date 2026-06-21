from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/products', methods=['GET', 'POST'])
def products():

    if request.method == 'POST':

        name = request.form['name']
        quantity = request.form['quantity']
        purchase_price = request.form['purchase_price']
        selling_price = request.form['selling_price']

        connection = sqlite3.connect('database/database.db')
        cursor = connection.cursor()

        cursor.execute(
            '''
            INSERT INTO products
            (name, quantity, purchase_price, selling_price)
            VALUES (?, ?, ?, ?)
            ''',
            (name, quantity, purchase_price, selling_price)
        )

        connection.commit()
        connection.close()

        return redirect('/products')

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM products')

    products_list = cursor.fetchall()

    connection.close()

    return render_template(
        'products.html',
        products=products_list
    )


@app.route('/delete_product/<int:id>')
def delete_product(id):

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    cursor.execute(
        'DELETE FROM products WHERE id=?',
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect('/products')


@app.route('/sales')
def sales():
    return render_template('sales.html')


@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__ == '__main__':
    app.run(debug=True)
