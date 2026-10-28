import math
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, ROUND_HALF_EVEN
from flask import Flask, render_template, request

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

def parse_number(raw):
    """Trả về (số, lỗi). Chấp nhận dấu phẩy thập phân (2,5)."""
    raw = (raw or "").strip()
    if not raw:
        return None, "Vui lòng nhập một số."
    try:
        n = float(raw.replace(",", "."))
    except ValueError:
        return None, "Vui lòng nhập một số."
    if not math.isfinite(n):  # chặn "inf", "nan"
        return None, "Vui lòng nhập một số."
    return n, None

def fmt(n):
    """3.0 -> 3, 3.5 -> 3.5, 0.30000000000000004 -> 0.3"""
    n = round(n, 10)
    return int(n) if n == int(n) else n

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    a = b = ""
    op = "+"
    result = None
    errors = {}

    if request.method == 'POST':
        a = request.form.get('a', '')
        b = request.form.get('b', '')
        op = request.form.get('op', '+')

        num_a, err_a = parse_number(a)
        num_b, err_b = parse_number(b)

        if err_a and err_b:
            errors['general'] = "Lỗi cả hai ô"
        if err_a:
            errors['a'] = err_a
        if err_b:
            errors['b'] = err_b

        if not errors:
            if op not in ('+', '-', '*', '/'):
                errors['general'] = "Phép toán không hợp lệ."
            elif op == '/' and num_b == 0:
                errors['b'] = "Không thể chia cho 0."
            else:
                res = {'+': num_a + num_b, '-': num_a - num_b,
                       '*': num_a * num_b}.get(op) if op != '/' else num_a / num_b
                result = f"{fmt(num_a)} {op} {fmt(num_b)} = {fmt(res)}"

    return render_template('calculator.html', shop=SHOP, a=a, b=b, op=op,
                           result=result, errors=errors)

# ---------- Bài 2: Tính điểm học phần ----------
GRADE_FIELDS = [("cc", "CC", "Chuyên cần", Decimal("0.1")),
                ("gk", "GK", "Giữa kỳ", Decimal("0.3")),
                ("ck", "CK", "Cuối kỳ", Decimal("0.6"))]

def validate_score(raw, label):
    """Hàm kiểm tra dùng chung cho cả 3 ô. Trả về (Decimal, lỗi)."""
    raw = (raw or "").strip()
    if not raw:
        return None, f"Lỗi ô {label}: Vui lòng nhập một số."
    try:
        n = Decimal(raw.replace(",", "."))
    except InvalidOperation:
        return None, f"Lỗi ô {label}: Vui lòng nhập một số."
    if not n.is_finite():
        return None, f"Lỗi ô {label}: Vui lòng nhập một số."
    if not (0 <= n <= 10):
        return None, f"Lỗi ô {label}: Điểm phải từ 0 đến 10."
    return n, None

def letter_grade(score, ck):
    if ck < 1:
        return "F"  # điểm liệt
    for threshold, letter in ((Decimal("8.5"), "A"), (Decimal("7.0"), "B"),
                              (Decimal("5.5"), "C"), (Decimal("4.0"), "D")):
        if score >= threshold:
            return letter
    return "F"

@app.route('/grade', methods=['GET', 'POST'])
def grade():
    values = {k: "" for k, _, _, _ in GRADE_FIELDS}
    errors = {}
    result = None

    if request.method == 'POST':
        nums = {}
        for key, label, _, _ in GRADE_FIELDS:
            values[key] = request.form.get(key, '')
            nums[key], err = validate_score(values[key], label)
            if err:
                errors[key] = err

        if len(errors) == 3 and all(not v.strip() for v in values.values()):
            errors['general'] = "Lỗi cả 3 ô"

        if not errors:
            total = sum(nums[k] * w for k, _, _, w in GRADE_FIELDS)
            score = total.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            letter = letter_grade(score, nums['ck'])
            note = "điểm thi dưới 1" if nums['ck'] < 1 else ""
            result = {"score": score, "letter": letter, "note": note}

    return render_template('grade.html', shop=SHOP, fields=GRADE_FIELDS,
                           values=values, errors=errors, result=result)

# ---------- Bài 3: Tính chỉ số BMI ----------
def validate_range(raw, label, lo, hi):
    """Kiểm tra số trong khoảng [lo, hi], chấp nhận dấu phẩy."""
    raw = (raw or "").strip()
    try:
        n = Decimal(raw.replace(",", "."))
        if not n.is_finite():
            raise InvalidOperation
    except InvalidOperation:
        return None, f"Lỗi ô {label}: Vui lòng nhập một số."
    if not (lo <= n <= hi):
        return None, f"Lỗi ô {label}: Giá trị phải từ {lo} đến {hi}."
    return n, None

def bmi_category(bmi):
    """Chuẩn người châu Á -> (tên nhóm, màu bootstrap)."""
    if bmi < Decimal("18.5"):
        return "Thiếu cân", "warning"
    if bmi < 23:
        return "Bình thường", "success"
    if bmi < 25:
        return "Thừa cân", "warning"
    return "Béo phì", "danger"

@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    height = weight = ""
    errors = {}
    result = None

    if request.method == 'POST':
        height = request.form.get('height', '')
        weight = request.form.get('weight', '')

        h, err_h = validate_range(height, "chiều cao", 50, 250)
        w, err_w = validate_range(weight, "cân nặng", 10, 300)
        if err_h:
            errors['height'] = err_h
            if h is None and height.strip() and err_h.endswith("từ 50 đến 250."):
                errors['height'] += " (nhập mét thay vì cm?)" if Decimal(height.strip().replace(",", ".")) < 3 else ""
        if err_w:
            errors['weight'] = err_w
        if not height.strip() and not weight.strip():
            errors['general'] = "Lỗi cả hai ô"

        if not errors:
            m = h / 100
            value = (w / (m * m)).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN)
            label, color = bmi_category(value)
            lo = (Decimal("18.5") * m * m).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            hi = (Decimal("22.9") * m * m).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            result = {"bmi": value, "label": label, "color": color, "lo": lo, "hi": hi}

    return render_template('bmi.html', shop=SHOP, height=height, weight=weight,
                           errors=errors, result=result)

# Trang 404 dùng chung base.html mà không cần tạo thêm file riêng
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', shop=SHOP), 404

if __name__ == '__main__':
    app.run(debug=True)