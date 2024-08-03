from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    items = db.relationship('InventoryItem', backref='user', lazy=True)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

db.create_all()

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    items = InventoryItem.query.filter_by(user_id=user.id).all()
    return render_template('index.html', user=user, items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        description = request.form['description']
        user_id = session['user_id']
        new_item = InventoryItem(name=name, quantity=quantity, description=description, user_id=user_id)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_item.html')

@app.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = InventoryItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.quantity = request.form['quantity']
        item.description = request.form['description']
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('update_item.html', item=item)

@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = InventoryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
