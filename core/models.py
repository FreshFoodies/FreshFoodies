from core import db, app
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

