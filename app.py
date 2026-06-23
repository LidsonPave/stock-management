from flask import Flask, render_template, request, redirect
import sqlite3
from flask import send_file
from pdf_generator import (
    generate_sales_pdf,
    generate_general_pdf,
    generate_entries_pdf,
    generate_low_stock_pdf,
    generate_cashflow_pdf
)
from flask import session
from flask import send_file
from flask import Flask, render_template, request, redirect, flash, get_flashed_messages
app = Flask(__name__)
app.secret_key = "chave_secreta_para_alertas"
@app.route('/')
def home():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM products
        WHERE quantity <= minimum_stock
        '''
    )

    low_stock_count = cursor.fetchone()[0]


    cursor.execute(
        '''
        SELECT
            products.name,
            stock_movements.movement_type,
            stock_movements.quantity,
            stock_movements.date

        FROM stock_movements

        INNER JOIN products
        ON products.id = stock_movements.product_id

        ORDER BY stock_movements.id DESC

        LIMIT 5
        '''
    )

    recent_movements = cursor.fetchall()

    cursor.execute(
        'SELECT COUNT(*) FROM products'
    )

    total_products = cursor.fetchone()[0]


    cursor.execute(
        'SELECT SUM(quantity) FROM products'
    )

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

        total_investment=round(total_investment, 2),

        total_sales_value=round(total_sales_value, 2),

        total_profit=round(total_profit, 2),

        low_stock_count=low_stock_count,

        recent_movements=recent_movements

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
        minimum_stock = request.form['minimum_stock']

        if product_id:

            cursor.execute(
                '''
                UPDATE products
                SET name=?, quantity=?, purchase_price=?, selling_price=?, minimum_stock=?
                WHERE id=?
                ''',
                (
                    name,
                    quantity,
                    purchase_price,
                    selling_price,
                    minimum_stock,
                    product_id
                )
            )

        else:

            cursor.execute(
                '''
                INSERT INTO products
                (name, quantity, purchase_price, selling_price, minimum_stock)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    name,
                    quantity,
                    purchase_price,
                    selling_price,
                    minimum_stock
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

@app.route('/entries', methods=['GET', 'POST'])
def entries():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    if request.method == 'POST':

        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])

        cursor.execute(
            '''
            UPDATE products
            SET quantity = quantity + ?
            WHERE id = ?
            ''',
            (quantity, product_id)
        )

        cursor.execute(
            '''
            INSERT INTO stock_movements
            (product_id, movement_type, quantity)
            VALUES (?, ?, ?)
            ''',
            (
                product_id,
                'Entrada',
                quantity
            )
        )

        connection.commit()

        return redirect('/entries')

    cursor.execute(
        '''
        SELECT id, name, quantity
        FROM products
        ORDER BY name
        '''
    )

    products = cursor.fetchall()

    cursor.execute(
        '''
        SELECT
            stock_movements.id,
            products.name,
            stock_movements.quantity,
            stock_movements.date

        FROM stock_movements

        INNER JOIN products
        ON products.id = stock_movements.product_id

        WHERE stock_movements.movement_type='Entrada'

        ORDER BY stock_movements.id DESC
        '''
    )

    movements = cursor.fetchall()

    connection.close()

    return render_template(
        'entries.html',
        products=products,
        movements=movements
     )
@app.route('/sales', methods=['GET', 'POST'])
def sales():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    if request.method == 'POST':

        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])

        # Busca o nome e a quantidade do produto para usar no alerta
        cursor.execute(
            '''
            SELECT name, quantity
            FROM products
            WHERE id = ?
            ''',
            (product_id,)
        )
        
        product_data = cursor.fetchone()
        product_name = product_data[0]
        current_stock = product_data[1]

        # TRAVA DE SEGURANÇA: Se tentar vender mais do que tem no estoque
        if quantity > current_stock:
            connection.close()
            flash(f"Estoque insuficiente para '{product_name}'! Você tentou vender {quantity}, mas só existem {current_stock} unidades.", "error")
            return redirect('/sales')

        # Se passou da trava, executa a venda normalmente
        if quantity <= current_stock:

            cursor.execute(
                '''
                UPDATE products
                SET quantity = quantity - ?
                WHERE id = ?
                ''',
                (quantity, product_id)
            )

            cursor.execute(
                '''
                SELECT selling_price
                FROM products
                WHERE id = ?
                ''',
                (product_id,)
            )

            selling_price = cursor.fetchone()[0]

            total_value = quantity * selling_price

            cursor.execute(
                '''
                INSERT INTO stock_movements
                (
                    product_id,
                    movement_type,
                    quantity,
                    total_value
                )
                VALUES (?, ?, ?, ?)
                ''',
                (
                    product_id,
                    'Saída',
                    quantity,
                    total_value
                )
            )

            connection.commit()

        connection.close()
        return redirect('/sales')

    # Código do método GET (Carregamento da página)
    cursor.execute(
        '''
        SELECT id, name, quantity
        FROM products
        ORDER BY name
        '''
    )
    products = cursor.fetchall()

    cursor.execute(
        '''
        SELECT
            stock_movements.id,
            products.name,
            stock_movements.quantity,
            stock_movements.date
        FROM stock_movements
        INNER JOIN products
        ON products.id = stock_movements.product_id
        WHERE stock_movements.movement_type='Saída'
        ORDER BY stock_movements.id DESC
        '''
    )
    movements = cursor.fetchall()

    connection.close()

    return render_template(
        'sales.html',
        products=products,
        movements=movements
    )


@app.route('/movements')
def movements():

    connection = sqlite3.connect('database/database.db')

    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT

            stock_movements.id,

            products.name,

            stock_movements.movement_type,

            stock_movements.quantity,

            stock_movements.date

        FROM stock_movements

        INNER JOIN products

        ON products.id = stock_movements.product_id

        ORDER BY stock_movements.id DESC
        '''
    )

    movements_list = cursor.fetchall()

    connection.close()

    return render_template(
        'movements.html',
        movements=movements_list
    )

@app.route('/cashflow', methods=['GET', 'POST'])
def cashflow():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    if request.method == 'POST':

        description = request.form['description']
        amount = float(request.form['amount'])

        cursor.execute(
            '''
            INSERT INTO cash_flow
            (description, amount)
            VALUES (?, ?)
            ''',
            (
                description,
                amount
            )
        )

        connection.commit()

        return redirect('/cashflow')


    cursor.execute(
        '''
        SELECT *
        FROM cash_flow
        ORDER BY id DESC
        '''
    )

    withdrawals = cursor.fetchall()


    cursor.execute(
        '''
        SELECT SUM(total_value)
        FROM stock_movements
        WHERE movement_type='Saída'
        '''
    )

    total_sales = cursor.fetchone()[0]

    if total_sales is None:
        total_sales = 0


    cursor.execute(
        '''
        SELECT SUM(amount)
        FROM cash_flow
        '''
    )

    total_withdrawals = cursor.fetchone()[0]

    if total_withdrawals is None:
        total_withdrawals = 0


    balance = total_sales - total_withdrawals

    connection.close()

    return render_template(
        'cashflow.html',
        withdrawals=withdrawals,
        total_sales=round(total_sales,2),
        total_withdrawals=round(total_withdrawals,2),
        balance=round(balance,2)
    )

@app.route('/reports')
def reports():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()


    # Produtos em estoque baixo

    cursor.execute(
        '''
        SELECT
            name,
            quantity,
            minimum_stock

        FROM products

        WHERE quantity <= minimum_stock
        '''
    )

    low_stock_products = cursor.fetchall()


    # Entradas

    cursor.execute(
        '''
        SELECT

            products.name,

            stock_movements.quantity,

            stock_movements.date

        FROM stock_movements

        INNER JOIN products

        ON products.id = stock_movements.product_id

        WHERE movement_type='Entrada'

        ORDER BY stock_movements.id DESC
        '''
    )

    entries = cursor.fetchall()


    # Saídas

    cursor.execute(
        '''
        SELECT

            products.name,

            stock_movements.quantity,

            stock_movements.total_value,

            stock_movements.date

        FROM stock_movements

        INNER JOIN products

        ON products.id = stock_movements.product_id

        WHERE movement_type='Saída'

        ORDER BY stock_movements.id DESC
        '''
    )

    sales = cursor.fetchall()

    connection.close()
    generate_sales_pdf(sales)

    return render_template(

        'reports.html',

        low_stock_products=low_stock_products,

        entries=entries,

        sales=sales

    )
@app.route('/export_sales_pdf')
def export_sales_pdf():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT
            products.name,
            stock_movements.quantity,
            stock_movements.total_value,
            stock_movements.date

        FROM stock_movements

        INNER JOIN products
        ON products.id = stock_movements.product_id

        WHERE movement_type='Saída'
        '''
    )

    sales = cursor.fetchall()

    connection.close()

    generate_sales_pdf(sales)

    return send_file(
        'relatorio.pdf',
        as_attachment=True
    )

@app.route('/export_general_pdf')
def export_general_pdf():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT COUNT(*) FROM products')
    total_products = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(quantity) FROM products')
    total_stock = cursor.fetchone()[0] or 0

    cursor.execute(
        'SELECT SUM(quantity * purchase_price) FROM products'
    )
    total_investment = cursor.fetchone()[0] or 0

    cursor.execute(
        '''
        SELECT SUM(total_value)
        FROM stock_movements
        WHERE movement_type="Saída"
        '''
    )
    total_sales = cursor.fetchone()[0] or 0

    cursor.execute(
        'SELECT SUM(amount) FROM cash_flow'
    )
    total_withdrawals = cursor.fetchone()[0] or 0

    connection.close()

    generate_general_pdf(
        total_products,
        total_stock,
        total_investment,
        total_sales,
        total_withdrawals
    )

    return send_file(
        'relatorio_geral.pdf',
        as_attachment=True
    )

@app.route('/export_entries_pdf')
def export_entries_pdf():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT
            products.name,
            stock_movements.quantity,
            stock_movements.date

        FROM stock_movements

        INNER JOIN products
        ON products.id = stock_movements.product_id

        WHERE movement_type='Entrada'

        ORDER BY stock_movements.id DESC
        '''
    )

    entries = cursor.fetchall()

    connection.close()

    generate_entries_pdf(entries)

    return send_file(
        'relatorio_entradas.pdf',
        as_attachment=True
    )


@app.route('/export_low_stock_pdf')
def export_low_stock_pdf():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT
            name,
            quantity,
            minimum_stock
        FROM products
        WHERE quantity <= minimum_stock
    ''')

    products = cursor.fetchall()

    connection.close()

    generate_low_stock_pdf(products)

    return send_file(
        'relatorio_estoque_baixo.pdf',
        as_attachment=True
    )

@app.route('/export_cashflow_pdf')
def export_cashflow_pdf():

    connection = sqlite3.connect('database/database.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT *
        FROM cash_flow
        ORDER BY id DESC
    ''')

    withdrawals = cursor.fetchall()

    cursor.execute('''
        SELECT SUM(total_value)
        FROM stock_movements
        WHERE movement_type='Saída'
    ''')

    total_sales = cursor.fetchone()[0]

    if total_sales is None:
        total_sales = 0

    cursor.execute('''
        SELECT SUM(amount)
        FROM cash_flow
    ''')

    total_withdrawals = cursor.fetchone()[0]

    if total_withdrawals is None:
        total_withdrawals = 0

    balance = total_sales - total_withdrawals

    connection.close()

    generate_cashflow_pdf(
        withdrawals,
        total_sales,
        total_withdrawals,
        balance
    )

    return send_file(
        'relatorio_fluxo_caixa.pdf',
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)
