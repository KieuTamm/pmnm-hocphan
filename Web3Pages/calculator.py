from flask import Flask, render_template, request

app = Flask(__name__)

def parse_number(val):
    if not val or not val.strip():
        return None, "Trống"
    # Chấp nhận dấu phẩy thập phân (thay , thành .)
    val_clean = val.strip().replace(',', '.')
    try:
        return float(val_clean), None
    except ValueError:
        return None, "Vui lòng nhập một số."

@app.route('/', methods=['GET', 'POST'])
def calculator():
    a_val = ""
    b_val = ""
    op_val = "+"
    result = None
    errors = {}

    if request.method == 'POST':
        a_val = request.form.get('a', '')
        b_val = request.form.get('b', '')
        op_val = request.form.get('op', '+')

        # Validate ô a và ô b
        num_a, err_a = parse_number(a_val)
        num_b, err_b = parse_number(b_val)

        if err_a:
            errors['a'] = "Vui lòng nhập một số." if err_a != "Trống" else "Lỗi ô a: Vui lòng nhập một số."
        if err_b:
            errors['b'] = "Vui lòng nhập một số." if err_b != "Trống" else "Lỗi ô b: Vui lòng nhập một số."

        # Trường hợp cả 2 ô đều trống/lỗi
        if err_a == "Trống" and err_b == "Trống":
            errors['general'] = "Lỗi cả hai ô"
        
        # Nếu không lỗi validate cơ bản thì kiểm tra phép toán & chia cho 0
        if not errors:
            if op_val not in ['+', '-', '*', '/']:
                errors['general'] = "Phép toán không hợp lệ."
            elif op_val == '/' and num_b == 0:
                errors['b'] = "Không thể chia cho 0."
            else:
                # Tính toán kết quả
                if op_val == '+':
                    res_num = num_a + num_b
                elif op_val == '-':
                    res_num = num_a - num_b
                elif op_val == '*':
                    res_num = num_a * num_b
                elif op_val == '/':
                    res_num = num_a / num_b
                
                # Format hiển thị số nguyên nếu là số nguyên (vd: 3.0 -> 3)
                fmt_a = int(num_a) if num_a.is_integer() else num_a
                fmt_b = int(num_b) if num_b.is_integer() else num_b
                fmt_res = int(res_num) if res_num.is_integer() else res_num

                result = f"{fmt_a} {op_val} {fmt_b} = {fmt_res}"

    return render_template('calculator.html', a=a_val, b=b_val, op=op_val, result=result, errors=errors)

if __name__ == '__main__':
    app.run(debug=True)