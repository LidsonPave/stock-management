from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


@app.route('/')
def home():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT COUNT(*) FROM products')
    total_products = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(quantity) FROM products')
    total_stock = cursor.fetchone()[0]

    cursor.execute(
        'SELECT SUM(quantity * purchase_price) FROM products'
    )
    total_investment = cursor.fetchone()[0]

    cursor.execute(
        'SELECT SUM(quantity * selling_price) FROM products'
    )
    total_sales_value = cursor.fetchone()[0]

    connection.close()

    if total_stock is None:
        total_stock = 0

    if total_investment is None:
        total_investment = 0

    if total_sales_value is None:
        total_sales_value = 0

    total_profit = total_sales_value - total_investment

    return render_template(
        'index.html',
        total_products=total_products,
        total_stock=total_stock,
        total_investment=total_investment,
        total_sales_value=total_sales_value,
        total_profit=total_profit
    )

@app.route('/products', methods=['GET', 'POST'])
def products():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    if request.method == 'POST':

        product_id = request.form.get('id')
        name = request.form['name']
        quantity = request.form['quantity']
        purchase_price = request.form['purchase_price']
        selling_price = request.form['selling_price']

        if product_id:

            cursor.execute(
                '''
                UPDATE products
                SET name=?, quantity=?, purchase_price=?, selling_price=?
                WHERE id=?
                ''',
                (
                    name,
                    quantity,
                    purchase_price,
                    selling_price,
                    product_id
                )
            )

        else:

            cursor.execute(
                '''
                INSERT INTO products
                (name, quantity, purchase_price, selling_price)
                VALUES (?, ?, ?, ?)
                ''',
                (
                    name,
                    quantity,
                    purchase_price,
                    selling_price
                )
            )

        connection.commit()

        return redirect('/products')

    search = request.args.get('search')

    if search:

        cursor.execute(
            '''
            SELECT *
            FROM products
            WHERE name LIKE ?
            ''',
            ('%' + search + '%',)
        )

    else:

        cursor.execute(
            'SELECT * FROM products'
        )

    products_list = cursor.fetchall()

    connection.close()

    return render_template(
        'products.html',
        products=products_list,
        edit_product=None
    )
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    if request.method == 'POST':

        name = request.form['name']
        quantity = request.form['quantity']
        purchase_price = request.form['purchase_price']
        selling_price = request.form['selling_price']

        cursor.execute(
            '''
            UPDATE products
            SET name=?, quantity=?, purchase_price=?, selling_price=?
            WHERE id=?
            ''',
            (
                name,
                quantity,
                purchase_price,
                selling_price,
                id
            )
        )

        connection.commit()
        connection.close()

        return redirect('/products')

    cursor.execute(
        'SELECT * FROM products WHERE id=?',
        (id,)
    )

    product = cursor.fetchone()

    cursor.execute(
        'SELECT * FROM products'
    )

    products_list = cursor.fetchall()

    connection.close()

    return render_template(
        'products.html',
        products=products_list,
        edit_product=product
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
