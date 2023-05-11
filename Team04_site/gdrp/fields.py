from django.db import models

# this class can hold a list of text separated by a given token (default ,)
class SeparatedTextField(models.TextField):

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return []
        return [item.strip() for item in value.split(self.token)]
    
    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is None:
            return[]
        return [item.strip() for item in value.split(self.token)]
    
    def get_prep_value(self, value):
        if isinstance(value, str):
            value = [item.strip() for item in value.split(self.token)]
        return self.token.join(value)
    
    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)