from core import db
from core.food.models import Category

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    expiration_date = db.Column(db.Date())
    time = db.Column(db.Time())
    category = db.Column(db.String, db.ForeignKey('category.id'))
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<ToDo {}>'.format(self.title)

# ctgry1 = Category(name='Fruits')
# ctgry2 = Category(name='Grains')
# ctgry3 = Category(name='Vegetables')
# ctgry4 = Category(name='Protein')
# ctgry5 = Category(name='Dairy')