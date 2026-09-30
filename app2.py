from flask import Flask, request, jsonify, url_for
from markupsafe import escape

app = Flask(__name__)

BOOKS = [
    {
        "id": 1,
        "title": "Lap trinh Python",
        "author": "An",
        "year": 2023,
        "category": "Lap trinh",
        "available": True,
    },
    {
        "id": 2,
        "title": "Flask Web",
        "author": "Binh",
        "year": 2024,
        "category": "Lap trinh",
        "available": False,
    },
    {
        "id": 3,
        "title": "Co so du lieu",
        "author": "Cuong",
        "year": 2022,
        "category": "CSDL",
        "available": True,
    },
    {
        "id": 4,
        "title": "Giai thuat",
        "author": "Dung",
        "year": 2021,
        "category": "Thuat toan",
        "available": True,
    },
]

CSS = """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: sans-serif;
    }
    body {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 20px;
    }
    nav {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #334155;
    }
    nav a {
        color: #38bdf8;
        text-decoration: none;
        font-weight: bold;
        margin-right: 20px;
    }
    nav a:hover {
        color: #818cf8;
    }
    h1 {
        font-size: 24px;
        margin-bottom: 15px;
        color: #f8fafc;
    }
    p {
        margin-bottom: 10px;
        color: #cbd5e1;
    }
    .box {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    .btn {
        display: inline-block;
        padding: 6px 12px;
        background-color: #334155;
        color: #fff;
        text-decoration: none;
        border-radius: 4px;
        margin-right: 5px;
    }
    .btn:hover {
        background-color: #38bdf8;
        color: #0f172a;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        background-color: #1e293b;
        border-radius: 8px;
        overflow: hidden;
    }
    th, td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #334155;
    }
    th {
        background-color: #0f172a;
        color: #38bdf8;
    }
    td a {
        color: #f43f5e;
        text-decoration: none;
        font-weight: bold;
    }
    td a:hover {
        text-decoration: underline;
    }
    .status-true {
        color: #4ade80;
        font-weight: bold;
    }
    .status-false {
        color: #f87171;
        font-weight: bold;
    }
</style>
"""


def menu():
    return f"""
    {CSS}
    <nav>
        <a href="{url_for('index')}">Trang chủ</a>
        <a href="{url_for('get_books')}">Danh sách sách</a>
        <a href="{url_for('api_books')}">API Books</a>
    </nav>
    """


@app.route("/")
def index():
    tong = len(BOOKS)
    san_sang = sum(1 for b in BOOKS if b["available"])

    return f"""
    {menu()}
    <div class="box">
        <h1>LibraryMS v0.1</h1>
        <p>Tổng số đầu sách: <b>{tong}</b></p>
        <p>Sách sẵn sàng cho mượn: <b>{san_sang}</b></p>
    </div>
    """


@app.route("/books")
def get_books():
    cat = request.args.get("category")
    list_sach = BOOKS

    thanh_loc = f"""
    <div class="box">
        <p>Lọc theo thể loại:</p>
        <a class="btn" href="{url_for('get_books')}">Tất cả</a>
        <a class="btn" href="{url_for('get_books', category='Lap trinh')}">Lập trình</a>
        <a class="btn" href="{url_for('get_books', category='CSDL')}">CSDL</a>
        <a class="btn" href="{url_for('get_books', category='Thuat toan')}">Thuật toán</a>
    """

    if cat:
        list_sach = [b for b in BOOKS if b["category"] == cat]
        thanh_loc += f"<p style='margin-top: 10px;'>Đang lọc: <b>{escape(cat)}</b></p>"

    thanh_loc += "</div>"

    rows = ""
    for b in list_sach:
        link = url_for("get_book_detail", book_id=b["id"])
        if b["available"]:
            tt = '<span class="status-true">Sẵn sàng</span>'
        else:
            tt = '<span class="status-false">Đã mượn</span>'

        rows += f"""
        <tr>
            <td>{b['id']}</td>
            <td><a href="{link}">{escape(b['title'])}</a></td>
            <td>{escape(b['author'])}</td>
            <td>{b['year']}</td>
            <td>{escape(b['category'])}</td>
            <td>{tt}</td>
        </tr>
        """

    html = f"""
    {menu()}
    <h1>Danh sách sách</h1>
    {thanh_loc}
    <table>
        <tr>
            <th>ID</th>
            <th>Tên sách</th>
            <th>Tác giả</th>
            <th>Năm</th>
            <th>Thể loại</th>
            <th>Trạng thái</th>
        </tr>
        {rows}
    </table>
    """
    return html


@app.route("/books/<int:book_id>")
def get_book_detail(book_id):
    for b in BOOKS:
        if b["id"] == book_id:
            if b["available"]:
                tt = '<span class="status-true">Sẵn sàng cho mượn</span>'
            else:
                tt = '<span class="status-false">Đã được mượn</span>'

            return f"""
            {menu()}
            <div class="box">
                <h1>{escape(b['title'])}</h1>
                <p>Tác giả: <b>{escape(b['author'])}</b></p>
                <p>Năm xuất bản: <b>{b['year']}</b></p>
                <p>Thể loại: <b>{escape(b['category'])}</b></p>
                <p>Trạng thái: {tt}</p>
            </div>
            """

    return (
        f"""
    {menu()}
    <div class="box">
        <h1>Lỗi 404</h1>
        <p>Không có sách với ID = {book_id}</p>
    </div>
    """,
        404,
    )


@app.route("/api/books")
def api_books():
    cat = request.args.get("category")
    if cat:
        return jsonify([b for b in BOOKS if b["category"] == cat])
    return jsonify(BOOKS)


@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    for b in BOOKS:
        if b["id"] == book_id:
            return jsonify(b)
    return jsonify({"error": f"Khong co sach voi ID = {book_id}"}), 404


@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Duong dan API khong ton tai"}), 404

    return (
        f"""
    {menu()}
    <div class="box">
        <h1>Lỗi 404</h1>
        <p>Trang không tồn tại!</p>
    </div>
    """,
        404,
    )


if __name__ == "__main__":
    app.run(debug=True)