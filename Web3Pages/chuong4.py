from flask import Flask, render_template

app = Flask(__name__)

SHOP = {
    "name": "N.O.A COFFEE",
    "address": "12 Lê Lợi, Huế",
    "phone": "0934 971 450"
}

MENU = [
    {"id": 1, "name": "Cà phê đen", "price": 20000, "image": "ca-phe-den.jpg"},
    {"id": 2, "name": "Cà phê sữa", "price": 25000, "image": "ca-phe-sua.jpg"},
    {"id": 3, "name": "Bạc xỉu", "price": 30000, "image": "bac-xiu.jpg"},
    {"id": 4, "name": "Trà đào", "price": 25000, "image": "tra-dao.jpg"},
    {"id": 5, "name": "Trà vải", "price": 25000, "image": "tra-vai.jpg"},
    {"id": 6, "name": "Sinh tố bơ", "price": 35000, "image": "sinh-to-bo.jpg"},
    {"id": 7, "name": "Nước cam", "price": 30000, "image": "nuoc-cam.jpg"}
]

@app.route('/')
def home():
    return render_template('index.html', shop=SHOP)

@app.route('/menu')
def menu():
    return render_template('menu.html', shop=SHOP, menu=MENU, total=len(MENU))

@app.route('/contact')
def contact():
    return render_template('contact.html', shop=SHOP)

# Trang 404 dùng chung base.html mà không cần tạo thêm file riêng
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', shop=SHOP), 404

if __name__ == '__main__':
    app.run(debug=True)