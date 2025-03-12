import os
from flask import Flask, render_template, redirect, url_for, request, flash
from models import *
from forms import *
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash , check_password_hash
from flask_login import login_user , LoginManager , logout_user, login_required



app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'

login_manager = LoginManager()
login_manager.init_app(app)  
login_manager.login_view = 'login'  

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config['SECRET_KEY'] = 'your_secret_key_here'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:4444@localhost/library_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)
migrate = Migrate(app, db)


# Pages Route
@app.route('/')
def home():
    books = db.session.query(Book).join(Author).all() 
    return render_template('index.html', books=books)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)

@app.route('/authors')
def authors():
    authors = Author.query.all()
    return render_template('authors.html', authors=authors)

@app.route('/author/<int:author_id>')
def author_detail(author_id):
    author = Author.query.get_or_404(author_id)
    books = Book.query.filter_by(author_id=author.id).all()
    return render_template('author_details.html', author=author, books=books)




# AUTHOR ( ADD , DELETE , UPDATE)
@app.route('/add_author', methods=['GET', 'POST'])
@login_required
def add_author():
    form = AuthorForm()
    if form.validate_on_submit():
        new_author = Author(name=form.name.data)
        db.session.add(new_author)
        db.session.commit()
        flash('Author added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_author.html', form=form)

@app.route('/edit_author/<int:author_id>', methods=['GET', 'POST'])
@login_required
def edit_author(author_id):
    author = Author.query.get_or_404(author_id)
    form = AuthorForm(obj=author)
    if form.validate_on_submit():
        author.name = form.name.data
        db.session.commit()
        flash("Author updated successfully!", "success")
        return redirect(url_for('home'))
    return render_template('edit_author.html', form=form, author=author)

@app.route('/delete_author/<int:author_id>', methods=['POST'])
@login_required
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    if author.books:
        flash("Cannot delete author with existing books!", "danger")
        return redirect(url_for('home'))

    db.session.delete(author)
    db.session.commit()
    flash("Author deleted successfully!", "danger")
    
    return redirect(url_for('home'))





# BOOK ( ADD , DELETE , UPDATE )
@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    form.author_id.choices = [(author.id, author.name) for author in Author.query.all()] 
    if form.validate_on_submit():
        file = form.img.data 
        filename = None
        if file:
            filename = secure_filename(file.filename)  
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_book = Book(
            name=form.name.data,
            publish_date=form.publish_date.data,
            price=form.price.data,
            appropriate=form.appropriate.data,
            author_id=form.author_id.data,
            img=filename 
        )

        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for('home'))

    return render_template('add_book.html', form=form)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.img:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], book.img)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!", "danger")

    return redirect(url_for('home'))

@app.route('/update_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm()
    form.author_id.choices = [(author.id, author.name) for author in Author.query.all()]
    
    if request.method == 'GET':
        form.name.data = book.name
        form.publish_date.data = book.publish_date
        form.price.data = book.price
        form.appropriate.data = book.appropriate
        form.author_id.data = book.author_id
    
    if form.validate_on_submit():
        book.name = form.name.data
        book.publish_date = form.publish_date.data
        book.price = form.price.data
        book.appropriate = form.appropriate.data
        book.author_id = form.author_id.data

        file = form.img.data
        if file:
            if book.img:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], book.img)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            book.img = filename 
        db.session.commit()
        flash("Book updated successfully!", "info")
        return redirect(url_for('home'))
    return render_template('update_book.html', form=form, book=book)




# USER  ( REGISTER , LOG IN , LOG OUT)
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already exists! Please use a different one.", "danger") 
            return render_template('register.html', form=form)
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('login')) 
    return render_template('register.html', form=form) 


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password", "danger")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()  
    flash('You have been logged out.', 'info') 
    return redirect(url_for('home'))  





# Run the application on local host, port 5000
if __name__ == '__main__':
    app.run(debug=True)
