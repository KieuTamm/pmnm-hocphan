from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key-quan-ly-sach"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
db.init_app(app)

class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    books: Mapped[list["Book"]] = relationship(back_populates="category", cascade="all, delete-orphan")

class Book(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    author: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(default=0.0)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["Category"] = relationship(back_populates="books")

with app.app_context():
    db.create_all()
    if db.session.scalar(db.select(func.count(Category.id))) == 0:
        c1 = Category(name="Công nghệ thông tin", description="Sách lập trình, CSDL, AI")
        c2 = Category(name="Văn học", description="Tiểu thuyết, truyện ngắn")
        c3 = Category(name="Kinh tế", description="Quản trị kinh doanh, tài chính")
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        db.session.add_all([
            Book(title="Lập trình Python cơ bản", author="Nguyễn Văn A", price=120000, category_id=c1.id),
            Book(title="Cơ sở dữ liệu SQLite", author="Trần Thị B", price=95000, category_id=c1.id),
            Book(title="Nhà Giả Kim", author="Paulo Coelho", price=79000, category_id=c2.id),
            Book(title="Cha Giàu Cha Nghèo", author="Robert Kiyosaki", price=110000, category_id=c3.id)
        ])
        db.session.commit()

@app.route("/")
def dashboard():
    total_categories = db.session.scalar(db.select(func.count(Category.id)))
    total_books = db.session.scalar(db.select(func.count(Book.id)))
    categories = db.session.scalars(db.select(Category)).all()
    recent_books = db.session.scalars(db.select(Book).order_by(Book.id.desc()).limit(5)).all()
    return render_template(
        "dashboard.html",
        total_categories=total_categories,
        total_books=total_books,
        categories=categories,
        recent_books=recent_books
    )

@app.route("/categories", methods=["GET", "POST"])
def manage_categories():
    error = None
    edit_id = request.args.get("edit", type=int)
    edit_cat = db.session.get(Category, edit_id) if edit_id else None

    if request.method == "POST":
        cat_id = request.form.get("id", type=int)
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            error = "Tên danh mục không được để trống"
        elif cat_id:
            cat = db.get_or_404(Category, cat_id)
            existing = db.session.scalar(db.select(Category).where(Category.name == name, Category.id != cat_id))
            if existing:
                error = "Tên danh mục đã tồn tại"
            else:
                cat.name = name
                cat.description = description
                db.session.commit()
                return redirect(url_for("manage_categories"))
        else:
            if db.session.scalar(db.select(Category).where(Category.name == name)):
                error = "Danh mục này đã tồn tại"
            else:
                db.session.add(Category(name=name, description=description))
                db.session.commit()
                return redirect(url_for("manage_categories"))

    categories = db.session.scalars(db.select(Category)).all()
    return render_template("categories.html", categories=categories, edit_cat=edit_cat, error=error)

@app.route("/categories/delete/<int:id>", methods=["POST"])
def delete_category(id):
    cat = db.get_or_404(Category, id)
    db.session.delete(cat)
    db.session.commit()
    return redirect(url_for("manage_categories"))

@app.route("/books", methods=["GET", "POST"])
def manage_books():
    error = None
    cat_filter = request.args.get("category_id", type=int)
    edit_id = request.args.get("edit", type=int)
    edit_book = db.session.get(Book, edit_id) if edit_id else None

    if request.method == "POST":
        book_id = request.form.get("id", type=int)
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        price_str = request.form.get("price", "0").strip()
        category_id = request.form.get("category_id", type=int)

        if not title or not author or not category_id:
            error = "Vui lòng nhập đủ thông tin sách và chọn danh mục"
        else:
            try:
                price = float(price_str)
                if book_id:
                    book = db.get_or_404(Book, book_id)
                    book.title = title
                    book.author = author
                    book.price = price
                    book.category_id = category_id
                else:
                    db.session.add(Book(title=title, author=author, price=price, category_id=category_id))
                db.session.commit()
                return redirect(url_for("manage_books", category_id=cat_filter or category_id))
            except ValueError:
                error = "Giá phải là số hợp lệ"

    categories = db.session.scalars(db.select(Category)).all()
    stmt = db.select(Book)
    if cat_filter:
        stmt = stmt.where(Book.category_id == cat_filter)
    books = db.session.scalars(stmt).all()

    return render_template(
        "books.html",
        books=books,
        categories=categories,
        cat_filter=cat_filter,
        edit_book=edit_book,
        error=error
    )

@app.route("/books/delete/<int:id>", methods=["POST"])
def delete_book(id):
    book = db.get_or_404(Book, id)
    cat_id = book.category_id
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("manage_books", category_id=cat_id))

if __name__ == "__main__":
    app.run(debug=True)