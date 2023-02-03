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
    foods = Food.query.all()
    date = datetime.now()
    now = date.strftime("%Y-%m-%d")

    form = FoodForm()
    form.category.choices =[(category.id, category.name) for category in Category.query.all()]

    if request.method == "POST":
        if request.form.get('foodDelete') is not None:
            deleteFood = request.form.get('checkedbox')
            if deleteFood is not None:
                foods = Food.query.filter_by(id=int(deleteFood)).one()
                db.session.delete(foods)
                db.session.commit()
                return redirect(url_for('food.foods'))
            else:
                check = 'Check off foods you have finished'

    elif form.validate_on_submit():
        selected= form.category.data
        category= Category.query.get(selected)
        foods = Food(title=form.title.data, date=form.expiration_date.data, time=form.time.data, category=category.name)
        db.session.add(foods)
        db.session.commit()
        return redirect(url_for('food.foods'))

    return render_template('food/foods.html', title='Add to Fridge', form=form, food=foods, DateNow=now, check=check)
