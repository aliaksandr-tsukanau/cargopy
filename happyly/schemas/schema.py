import marshmallow


class Schema(marshmallow.Schema):
    """
    Marshmallow schema, which raises errors on mismatch
    (extra fields provided also raise exception).

    Subclass it just like any marshmallow Schema to describe schema.

    Instantiation with no arguments is a good strict default,
    but you can pass any arguments valid for `marshmallow.Schema`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(strict=True, *args, **kwargs)

    @marshmallow.validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = set(original_data) - set(self.fields)
        if unknown:
            raise marshmallow.ValidationError('Unknown field', unknown)
