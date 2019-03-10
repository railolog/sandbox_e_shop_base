from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Введите логин', validators=[DataRequired()])
    password = PasswordField('Придумайте пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')


class AddGoodsForm(FlaskForm):
    type = RadioField('Категория:', choices=[('gpu', 'Видеокарта'),
                                             ('motherboard', 'Материнская плата'),
                                             ('cpu', 'ЦП'),
                                             ('ram', 'ОЗУ'),
                                             ('memory_drivers', 'Накопители памяти'),
                                             ('cooling_system', 'Системы охлаждения'),
                                             ('power_supply', 'БП'),
                                             ('computer_case', 'Корпуса'),
                                             ('thermal_paste', 'Термопасты')],
                      validators=[DataRequired()])
    name = StringField('Наименование товара:', validators=[DataRequired()])
    description = TextAreaField('Описание товара', validators=[DataRequired()])
    price = StringField('Цена товара в рублях', validators=[DataRequired()])
    file_upload = FileField('Фото', validators=[
                                    FileRequired(),
                                    FileAllowed(['jpg', 'png'], 'Images only!')
                                                ])
    submit = SubmitField('Добавить товар в номенклатуру')


class AddPhotoForm(FlaskForm):
    photo_upload = FileField('Фото', validators=[
                                    FileRequired(),
                                    FileAllowed(['jpg', 'png'], 'Images only!')
                                                ])
    submit = SubmitField('Добавить')
