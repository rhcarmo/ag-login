import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'qwemnb235647'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Contacts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))
	phone = db.Column(db.String(100))
	image = db.Column(db.String(100))
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	created_at = db.Column(db.String(50))
	updated_at = db.Column(db.String(50))

class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	created_at = db.Column(db.String(50))
	updated_at = db.Column(db.String(50))

@app.route('/')
def index():
	if 'user_id' not in session:
		return redirect('/login')

	title = 'Agenda de Contatos'
	contacts = Contacts.query.filter_by(
		user_id=session['user_id']
	).all()

	return render_template(
		'index.html',
		title=title,
		contacts=contacts
	)

@app.route('/create', methods=['POST'])
def create():
	if 'user_id' not in session:
		return redirect('/login')

	name = request.form.get('name')
	email = request.form.get('email')
	phone = request.form.get('phone')
	new_contact = Contacts(
		name=name, 
		email=email, 
		phone=phone, 
		user_id=session['user_id']
	)
	db.session.add(new_contact)
	db.session.commit()
	return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
	if 'user_id' not in session:
		return redirect('/login')

	contacts = Contacts.query.filter_by(id=id).filter_by(user_id=session['user_id']).first()
	db.session.delete(contacts)
	db.session.commit()
	return redirect('/')

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
	name = request.form.get('name')
	email = request.form.get('email')
	phone = request.form.get('phone')
	contacts = Contacts.query.filter_by(id=id).first()
	contacts.name = name
	contacts.email = email
	contacts.phone = phone
	db.session.commit()
	return redirect('/')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/signin', methods=['POST'])
def signin():
	email = request.form.get('email')
	password = request.form.get('password')

	user = Users.query.filter_by(email=email).first()
	if not user:
		return redirect('/login')
	if not check_password_hash(user.password, password):
		return redirect('/login')
	
	session['user_id'] = user.id
	return redirect('/')

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/signup', methods=['POST'])
def signup():
	name = request.form.get('name')
	email = request.form.get('email')
	password = request.form.get('password')

	user = Users.query.filter_by(email=email).first()
	if user:
		return redirect('/register')
	
	new_user = Users(name=name, email=email, password=generate_password_hash(password, method='sha256'))
	db.session.add(new_user)
	db.session.commit()
	return redirect('/login')

@app.route('/logout')
def logout():
	session.pop('user_id', None)
	return redirect('/login')

if __name__ == '__main__':
	db.create_all()

	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0',port=port)