from flask_wtf import FlaskForm
from wtforms import StringField, TimeField, DateField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class FoodForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    category = SelectField('Category', coerce=int , validators=[DataRequired()])
    expiration_date = DateField('Date', format='%Y-%m-%d' , validators=[DataRequired()])
    time = TimeField('Time', format='%H:%M' , validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    submit = SubmitField('Add Food')

"""
class DollarField(DecimalField):
    def process_formdata(self, valuelist):
        if len(valuelist) == 1:
            self.data = [valuelist[0].strip('$').replace(',', '')]
        else:
            self.data = []

        # Calls "process_formdata" on the parent types of "DollarField",
        # which includes "DecimalField"
        super(DollarField).process_formdata(self.data)
"""