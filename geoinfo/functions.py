from django.db.models import Func, Transform, Value, fields


class CastGeometry(Func):
    """
    Coerce an expression to a postgis geometry type
    """
    function = 'CAST'
    template = '%(function)s(%(expressions)s AS %(db_type)s)'

    def __init__(self, expression, output_field):
        super(CastGeometry, self).__init__(expression, output_field=output_field)

    # modified to work with django 1.8
    def as_sql(self, compiler, connection, **extra_context):
        # if 'db_type' not in extra_context:
        #     extra_context['db_type'] = self._output_field.db_type(connection)
        return super(CastGeometry, self).as_sql(compiler, connection, **extra_context)

    def as_postgresql(self, compiler, connection):
        # CAST would be valid too, but the :: shortcut syntax is more readable.
        # return self.as_sql(compiler, connection, template='%(expressions)s::%(db_type)s')
        return self.as_sql(compiler, connection, template='%(expressions)s::geometry')

