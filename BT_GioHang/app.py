import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, func
from forms import CheckoutForm, BookForm, CategoryForm

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()

app = Flask(__name__)
app.config["SECRET_KEY"] = "nha-sach-song-huong"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///songhuong.db"
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

db.init_app(app)
csrf.init_app(app)

class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    books: Mapped[list["Book"]] = relationship(back_populates="category")

class Book(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), unique=True)
    author: Mapped[str] = mapped_column(String(100))
    publisher: Mapped[str] = mapped_column(String(100), default="NXB Đại học Huế")
    year: Mapped[int] = mapped_column(Integer, default=2024)
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(Text, default="")
    cover: Mapped[str] = mapped_column(String(255), default="")
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["Category"] = relationship(back_populates="books")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="book")

class Order(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(120), default="")
    address: Mapped[str] = mapped_column(String(255))
    note: Mapped[str] = mapped_column(String(255), default="")
    payment_method: Mapped[str] = mapped_column(String(20), default="COD")
    shipping_fee: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="Chờ xác nhận")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    history: Mapped[str] = mapped_column(Text, default="")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

class OrderItem(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)
    order: Mapped["Order"] = relationship(back_populates="items")
    book: Mapped["Book"] = relationship(back_populates="order_items")

with app.app_context():
    os.makedirs("static/uploads", exist_ok=True)
    db.create_all()
    if db.session.scalar(db.select(func.count(Category.id))) == 0:
        c1 = Category(name="Lập trình")
        c2 = Category(name="Cơ sở dữ liệu")
        c3 = Category(name="Công cụ")
        c4 = Category(name="Mạng")
        c5 = Category(name="Kỹ năng lập trình")
        db.session.add_all([c1, c2, c3, c4, c5])
        db.session.commit()

        db.session.add_all([
            Book(title="Lập trình Python cơ bản", author="Nguyễn Văn A", publisher="NXB Đại học Huế", year=2024, price=95000, stock=30, description="Giáo trình Python cơ bản.", category_id=c1.id),
            Book(title="Giáo trình Flask", author="Miguel Grinberg", publisher="O'Reilly", year=2023, price=120000, stock=20, description="Lập trình web với Flask.", category_id=c1.id),
            Book(title="Cơ sở dữ liệu", author="Trần Văn B", publisher="NXB Giáo dục", year=2022, price=85000, stock=0, description="Giáo trình cơ sở dữ liệu.", category_id=c2.id),
            Book(title="Pro Git", author="Scott Chacon", publisher="Apress", year=2021, price=150000, stock=15, description="Hướng dẫn sử dụng Git.", category_id=c3.id),
            Book(title="Mạng máy tính", author="Lê Văn C", publisher="NXB ĐHQG", year=2023, price=110000, stock=12, description="Kiến thức mạng máy tính.", category_id=c4.id),
            Book(title="Clean Code", author="Robert C. Martin", publisher="Prentice Hall", year=2008, price=180000, stock=5, description="Viết mã sạch chuyên nghiệp.", category_id=c5.id),
        ])
        db.session.commit()

def get_cart_count():
    cart = session.get("cart", {})
    total = 0
    for qty in cart.values():
        total += qty
    return total

def get_pending_count():
    return db.session.scalar(db.select(func.count(Order.id)).where(Order.status == "Chờ xác nhận")) or 0

@app.route("/")
@app.route("/books")
def book_list():
    q = request.args.get("q", "").strip()
    cat_id = request.args.get("category_id", type=int)

    stmt = db.select(Book)
    if q:
        stmt = stmt.where(Book.title.ilike(f"%{q}%") | Book.author.ilike(f"%{q}%"))
    if cat_id:
        stmt = stmt.where(Book.category_id == cat_id)

    books = db.session.scalars(stmt).all()
    categories = db.session.scalars(db.select(Category)).all()
    return render_template("shop.html", view="list", books=books, categories=categories, q=q, cat_id=cat_id, cart_count=get_cart_count())

@app.route("/books/<int:id>")
def book_detail(id):
    book = db.get_or_404(Book, id)
    cart = session.get("cart", {})
    in_cart = cart.get(str(book.id), 0)
    max_add = book.stock - in_cart
    if max_add < 0:
        max_add = 0
    return render_template("shop.html", view="detail", book=book, in_cart=in_cart, max_add=max_add, cart_count=get_cart_count())

@app.route("/cart/add/<int:id>", methods=["POST"])
def cart_add(id):
    book = db.get_or_404(Book, id)
    qty = request.form.get("qty", 1, type=int)
    next_url = request.form.get("next") or "/books"

    cart = session.get("cart", {})
    current_qty = cart.get(str(id), 0)

    if qty < 1 or current_qty + qty > book.stock:
        flash("Số lượng không hợp lệ hoặc vượt quá tồn kho.", "danger")
        return redirect(next_url)

    cart[str(id)] = current_qty + qty
    session["cart"] = cart
    flash(f"✓ Đã thêm {qty} × {book.title} vào giỏ hàng.", "success")
    return redirect(next_url)

@app.route("/cart")
def cart_view():
    cart = session.get("cart", {})
    items = []
    subtotal = 0

    for book_id, qty in cart.items():
        book = db.session.get(Book, int(book_id))
        if book:
            line_total = book.price * qty
            subtotal += line_total
            items.append({"book": book, "qty": qty, "line_total": line_total})

    return render_template("cart.html", view="cart", items=items, subtotal=subtotal, cart_count=get_cart_count())

@app.route("/cart/update/<int:id>", methods=["POST"])
def cart_update(id):
    book = db.get_or_404(Book, id)
    action = request.form.get("action")
    cart = session.get("cart", {})
    key = str(id)

    if key in cart:
        if action == "inc" and cart[key] < book.stock:
            cart[key] += 1
        elif action == "dec":
            cart[key] -= 1
            if cart[key] <= 0:
                del cart[key]
        elif action == "remove":
            del cart[key]

    session["cart"] = cart
    return redirect("/cart")

@app.route("/cart/clear", methods=["POST"])
def cart_clear():
    session.pop("cart", None)
    return redirect("/cart")

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("Giỏ hàng đang trống.", "warning")
        return redirect("/cart")

    items = []
    subtotal = 0
    for book_id, qty in cart.items():
        book = db.session.get(Book, int(book_id))
        if book:
            line_total = book.price * qty
            subtotal += line_total
            items.append({"book": book, "qty": qty, "line_total": line_total})

    shipping = 0 if subtotal >= 200000 else 20000
    total = subtotal + shipping

    form = CheckoutForm()
    if form.validate_on_submit():
        for item in items:
            if item["qty"] > item["book"].stock:
                flash(f"Sách '{item['book'].title}' không đủ hàng trong kho!", "danger")
                return redirect("/cart")

        order = Order(
            customer_name=form.customer_name.data,
            phone=form.phone.data,
            email=form.email.data or "",
            address=form.address.data,
            note=form.note.data or "",
            payment_method=form.payment_method.data,
            shipping_fee=shipping,
            total_amount=total,
            status="Chờ xác nhận",
            history=datetime.now().strftime("%d/%m %H:%M") + " · Đặt hàng"
        )
        db.session.add(order)
        db.session.commit()

        for item in items:
            book = item["book"]
            book.stock -= item["qty"]
            order_item = OrderItem(
                order_id=order.id,
                book_id=book.id,
                quantity=item["qty"],
                unit_price=book.price
            )
            db.session.add(order_item)

        db.session.commit()
        session.pop("cart", None)
        return redirect(f"/orders/{order.id}")

    return render_template("cart.html", view="checkout", form=form, items=items, subtotal=subtotal, shipping=shipping, total=total, cart_count=get_cart_count())

@app.route("/orders/<int:id>")
def order_success(id):
    order = db.get_or_404(Order, id)
    return render_template("cart.html", view="success", order=order, cart_count=get_cart_count())

@app.route("/admin")
def admin_dashboard():
    total_books = db.session.scalar(db.select(func.count(Book.id))) or 0
    pending_count = get_pending_count()
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    month_revenue = db.session.scalar(
        db.select(func.sum(Order.total_amount)).where(Order.status == "Hoàn tất", Order.created_at >= month_start)
    ) or 0
    low_stock_books = db.session.scalars(db.select(Book).where(Book.stock <= 5)).all()
    recent_orders = db.session.scalars(db.select(Order).order_by(Order.id.desc()).limit(5)).all()

    return render_template(
        "admin.html",
        view="dashboard",
        total_books=total_books,
        pending_count=pending_count,
        pending_orders=pending_count,
        month_revenue=month_revenue,
        low_stock_books=low_stock_books,
        recent_orders=recent_orders,
        current_month=now.month
    )

@app.route("/admin/books")
def admin_books():
    q = request.args.get("q", "").strip()
    cat_id = request.args.get("category_id", type=int)
    stock_filter = request.args.get("stock", "")
    page = request.args.get("page", 1, type=int)

    stmt = db.select(Book).order_by(Book.id.desc())
    if q:
        stmt = stmt.where(Book.title.ilike(f"%{q}%") | Book.author.ilike(f"%{q}%"))
    if cat_id:
        stmt = stmt.where(Book.category_id == cat_id)
    if stock_filter == "in":
        stmt = stmt.where(Book.stock > 5)
    elif stock_filter == "low":
        stmt = stmt.where(Book.stock > 0, Book.stock <= 5)
    elif stock_filter == "out":
        stmt = stmt.where(Book.stock == 0)

    pagination = db.paginate(stmt, page=page, per_page=5, error_out=False)
    categories = db.session.scalars(db.select(Category)).all()
    return render_template(
        "admin.html",
        view="books",
        pagination=pagination,
        categories=categories,
        q=q,
        cat_id=cat_id,
        stock_filter=stock_filter,
        pending_orders=get_pending_count()
    )

@app.route("/admin/books/new", methods=["GET", "POST"])
def admin_book_new():
    form = BookForm()
    categories = db.session.scalars(db.select(Category)).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        title = form.title.data.strip()
        existed = db.session.scalar(db.select(Book).where(func.lower(Book.title) == title.lower()))
        if existed:
            form.title.errors.append("Tên sách đã tồn tại.")
        else:
            filename = ""
            if form.cover.data:
                ext = os.path.splitext(form.cover.data.filename)[1]
                filename = uuid.uuid4().hex + ext
                form.cover.data.save(os.path.join("static/uploads", filename))

            book = Book(
                title=title,
                author=form.author.data.strip(),
                category_id=form.category_id.data,
                publisher=form.publisher.data or "",
                year=form.year.data or 2024,
                price=form.price.data,
                stock=form.stock.data,
                description=form.description.data or "",
                cover=filename
            )
            db.session.add(book)
            db.session.commit()
            flash("Đã thêm sách mới.", "success")
            return redirect("/admin/books")

    return render_template("admin.html", view="book_form", form=form, book=None, pending_orders=get_pending_count())

@app.route("/admin/books/<int:id>/edit", methods=["GET", "POST"])
def admin_book_edit(id):
    book = db.get_or_404(Book, id)
    form = BookForm(obj=book)
    categories = db.session.scalars(db.select(Category)).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        title = form.title.data.strip()
        existed = db.session.scalar(db.select(Book).where(func.lower(Book.title) == title.lower(), Book.id != id))
        if existed:
            form.title.errors.append("Tên sách đã tồn tại.")
        else:
            book.title = title
            book.author = form.author.data.strip()
            book.category_id = form.category_id.data
            book.publisher = form.publisher.data or ""
            book.year = form.year.data or 2024
            book.price = form.price.data
            book.stock = form.stock.data
            book.description = form.description.data or ""

            if form.cover.data:
                if book.cover and os.path.exists("static/uploads/" + book.cover):
                    os.remove("static/uploads/" + book.cover)
                ext = os.path.splitext(form.cover.data.filename)[1]
                filename = uuid.uuid4().hex + ext
                form.cover.data.save("static/uploads/" + filename)
                book.cover = filename

            db.session.commit()
            flash("Đã cập nhật sách.", "success")
            return redirect("/admin/books")

    return render_template("admin.html", view="book_form", form=form, book=book, pending_orders=get_pending_count())

@app.route("/admin/books/<int:id>/delete", methods=["POST"])
def admin_book_delete(id):
    book = db.get_or_404(Book, id)
    if len(book.order_items) > 0:
        flash("Không thể xoá sách đã có trong đơn hàng.", "danger")
        return redirect("/admin/books")
    if book.cover and os.path.exists("static/uploads/" + book.cover):
        os.remove("static/uploads/" + book.cover)
    db.session.delete(book)
    db.session.commit()
    flash("Đã xoá sách.", "success")
    return redirect("/admin/books")

@app.route("/admin/categories", methods=["GET", "POST"])
def admin_categories():
    edit_id = request.args.get("edit", type=int)
    edit_cat = db.session.get(Category, edit_id) if edit_id else None
    form = CategoryForm(obj=edit_cat)

    if form.validate_on_submit():
        name = form.name.data.strip()
        cat_id = request.form.get("cat_id", type=int)
        if cat_id:
            cat = db.get_or_404(Category, cat_id)
            existed = db.session.scalar(db.select(Category).where(func.lower(Category.name) == name.lower(), Category.id != cat_id))
            if existed:
                form.name.errors.append("Danh mục đã tồn tại.")
            else:
                cat.name = name
                cat.description = form.description.data or ""
                db.session.commit()
                flash("Đã cập nhật danh mục.", "success")
                return redirect("/admin/categories")
        else:
            existed = db.session.scalar(db.select(Category).where(func.lower(Category.name) == name.lower()))
            if existed:
                form.name.errors.append("Danh mục đã tồn tại.")
            else:
                db.session.add(Category(name=name, description=form.description.data or ""))
                db.session.commit()
                flash("Đã thêm danh mục.", "success")
                return redirect("/admin/categories")

    rows = db.session.execute(
        db.select(Category, func.count(Book.id)).outerjoin(Book).group_by(Category.id)
    ).all()
    return render_template("admin.html", view="categories", rows=rows, form=form, edit_cat=edit_cat, pending_orders=get_pending_count())

@app.route("/admin/categories/<int:id>/delete", methods=["POST"])
def admin_category_delete(id):
    cat = db.get_or_404(Category, id)
    if len(cat.books) > 0:
        flash(f"✗ Không thể xoá \"{cat.name}\": còn {len(cat.books)} sách.", "danger")
        return redirect("/admin/categories")
    db.session.delete(cat)
    db.session.commit()
    flash("Đã xoá danh mục.", "success")
    return redirect("/admin/categories")

@app.route("/admin/orders")
def admin_orders():
    status = request.args.get("status", "")
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    counts_raw = db.session.execute(db.select(Order.status, func.count(Order.id)).group_by(Order.status)).all()
    status_counts = dict(counts_raw)
    total_all = sum(status_counts.values())

    stmt = db.select(Order).order_by(Order.id.desc())
    if status:
        stmt = stmt.where(Order.status == status)
    if q:
        q_num = q.replace("#", "")
        if q_num.isdigit():
            stmt = stmt.where((Order.id == int(q_num)) | Order.customer_name.ilike(f"%{q}%") | Order.phone.ilike(f"%{q}%"))
        else:
            stmt = stmt.where(Order.customer_name.ilike(f"%{q}%") | Order.phone.ilike(f"%{q}%"))

    all_filtered = db.session.scalars(stmt).all()
    filtered_count = len(all_filtered)
    filtered_sum = sum(o.total_amount for o in all_filtered)
    pagination = db.paginate(stmt, page=page, per_page=10, error_out=False)

    return render_template(
        "admin.html",
        view="orders",
        pagination=pagination,
        status=status,
        q=q,
        status_counts=status_counts,
        total_all=total_all,
        filtered_count=filtered_count,
        filtered_sum=filtered_sum,
        pending_orders=get_pending_count()
    )

@app.route("/admin/orders/<int:id>", methods=["GET", "POST"])
def admin_order_detail(id):
    order = db.get_or_404(Order, id)
    if request.method == "POST":
        new_status = request.form.get("status")
        valid = False
        if order.status == "Chờ xác nhận" and new_status in ["Đang giao", "Đã huỷ"]:
            valid = True
        elif order.status == "Đang giao" and new_status in ["Hoàn tất", "Đã huỷ"]:
            valid = True

        if not valid:
            flash("Chuyển trạng thái không hợp lệ!", "danger")
            return redirect(f"/admin/orders/{id}")

        if new_status == "Đã huỷ":
            for item in order.items:
                item.book.stock += item.quantity

        order.status = new_status
        order.history += "\n" + datetime.now().strftime("%d/%m %H:%M") + " · " + new_status
        db.session.commit()
        flash("Đã cập nhật trạng thái đơn hàng.", "success")
        return redirect(f"/admin/orders/{id}")

    return render_template("admin.html", view="order_detail", order=order, pending_orders=get_pending_count())

if __name__ == "__main__":
    app.run(debug=True)