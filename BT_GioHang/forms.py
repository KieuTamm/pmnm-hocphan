from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SelectField, RadioField, SubmitField
from wtforms.validators import DataRequired, Regexp, Optional, Email, NumberRange

class CheckoutForm(FlaskForm):
    customer_name = StringField("Họ tên *", validators=[DataRequired(message="Vui lòng nhập họ tên")])
    phone = StringField("Số điện thoại *", validators=[
        DataRequired(message="Vui lòng nhập SĐT"),
        Regexp(r"^0\d{9}$", message="Số điện thoại gồm 10 chữ số, bắt đầu bằng 0.")
    ])
    email = StringField("Email", validators=[Optional(), Email(message="Email không đúng định dạng")])
    address = StringField("Địa chỉ giao hàng *", validators=[DataRequired(message="Vui lòng nhập địa chỉ")])
    note = StringField("Ghi chú", validators=[Optional()])
    payment_method = RadioField("Thanh toán *", choices=[
        ("COD", "Tiền mặt khi nhận hàng"),
        ("BANK", "Chuyển khoản")
    ], default="COD")
    submit = SubmitField("Xác nhận đặt hàng")

class BookForm(FlaskForm):
    title = StringField("Tên sách *", validators=[DataRequired(message="Tên sách bắt buộc")])
    author = StringField("Tác giả *", validators=[DataRequired(message="Tác giả bắt buộc")])
    category_id = SelectField("Danh mục *", coerce=int)
    publisher = StringField("Nhà xuất bản", validators=[Optional()])
    year = IntegerField("Năm xuất bản", validators=[Optional(), NumberRange(min=1900, max=2026)])
    price = FloatField("Giá (đồng) *", validators=[DataRequired(message="Giá bắt buộc"), NumberRange(min=1000, message="Giá >= 1.000 đ")])
    stock = IntegerField("Tồn kho *", validators=[NumberRange(min=0, message="Tồn kho không âm.")], default=0)
    description = TextAreaField("Mô tả", validators=[Optional()])
    cover = FileField("Ảnh bìa", validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], "Chỉ nhận JPG, PNG, WEBP")])
    submit = SubmitField("Lưu")

class CategoryForm(FlaskForm):
    name = StringField("Tên *", validators=[DataRequired(message="Tên danh mục bắt buộc")])
    description = TextAreaField("Mô tả", validators=[Optional()])
    submit = SubmitField("+ Thêm")