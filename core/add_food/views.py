from flask import render_template, redirect, url_for, request
from .models import Category
from ..models import Food
from . import food
from .forms import FoodForm
from .. import db
from datetime import datetime

@food.route('/add-food', methods=['GET', 'POST'])
def foods():
    check = None
    todo = Food.query.all()
    date = datetime.now()
    now = date.strftime("%Y-%m-%d")

    form = FoodForm()
    form.category.choices =[(category.id, category.name) for category in Category.query.all()]

    if request.method == "POST":
        if request.form.get('foodDelete') is not None:
            deleteFood = request.form.get('checkedbox')
            if deleteFood is not None:
                todo = Food.query.filter_by(id=int(deleteFood)).one()
                db.session.delete(todo)
                db.session.commit()
                return redirect(url_for('food.foods'))
            else:
                check = 'Please check-box of task to be deleted'

    elif form.validate_on_submit():
        selected= form.category.data
        category= Category.query.get(selected)
        todo = Food(title=form.title.data, date=form.date.data, time= form.time.data, category= category.name)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('food.foods'))

    return render_template('foods.html', title='Add Food', form=form, todo=todo, DateNow=now, check=check)
