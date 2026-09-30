from flask import Flask, request, url_for

app = Flask(__name__)

# 1. Trang chủ
@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return f"<a href='/'>Trang chủ</a> | <a href='{url_for('gioi_thieu')}'>Giới thiệu</a>"

# 2. Trang Giới thiệu
@app.route("/gioi-thieu")
@app.route("/about")
def gioi_thieu():
    return "Xin chào, đây là trang giới thiệu!"

# 3. Tính tổng chuỗi số (ví dụ: /sum/1,2,3)
@app.route("/sum/<strs>")
def tong(strs):
    numbers = strs.split(",")
    total = sum(float(num) for num in numbers)
    return f"Tong cua {strs} la {total}"

# 4. Tính toán theo tham số URL (ví dụ: /tinh-toan?a=5&b=3&op=add)
@app.route("/tinh-toan")
def tinh_toan():
    a = request.args.get("a")
    b = request.args.get("b")
    op = request.args.get("op")
    
    if not a or not b:
        return "Vui long truyen du tham so a va b!"
        
    if op == "add":
        return f"{a} + {b} = {float(a) + float(b)}"
    elif op == "sub":
        return f"{a} - {b} = {float(a) - float(b)}"
    else:
        return "Vui long truyen tham so op hop le ('add' hoac 'sub')!"

# 5. Bình phương số thực (ví dụ: /square/5.0)
@app.route("/square/<float:x>")
def square(x):
    return f"Gtri bp {x} la {x**2}"

if __name__ == "__main__":
    app.run(debug=True)  # Bật True để code tự reload khi sửa