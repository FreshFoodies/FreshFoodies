from core import db

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    expiration_date = db.Column(db.Date())
    time = db.Column(db.Time())
    category= db.Column(db.String, db.ForeignKey('category.id'))

    def __repr__(self):
        return '<ToDo {}>'.format(self.title)