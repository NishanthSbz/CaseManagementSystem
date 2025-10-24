from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from datetime import datetime, timezone

class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(validate=validate.OneOf(['admin', 'user']), missing='user')

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class CaseCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(missing='')
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']), missing='medium')
    status = fields.Str(validate=validate.OneOf(['open', 'in_progress', 'closed']), missing='open')
    due_date = fields.DateTime(allow_none=True)
    assigned_to = fields.Int(allow_none=True)
    
    @validates('due_date')
    def validate_due_date(self, value):
        if value:
            now = datetime.now(timezone.utc)
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            elif value.tzinfo != timezone.utc:
                value = value.astimezone(timezone.utc)
            
            if value <= now:
                raise ValidationError('Due date must be in the future')

class CaseUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str()
    status = fields.Str(validate=validate.OneOf(['open', 'in_progress', 'closed']))
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']))
    due_date = fields.DateTime(allow_none=True)
    assigned_to = fields.Int(allow_none=True)
    
    @validates('due_date')
    def validate_due_date(self, value):
        if value:
            now = datetime.now(timezone.utc)
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            elif value.tzinfo != timezone.utc:
                value = value.astimezone(timezone.utc)
            
            if value <= now:
                raise ValidationError('Due date must be in the future')

class CaseQuerySchema(Schema):
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=10)
    status = fields.Str(validate=validate.OneOf(['open', 'in_progress', 'closed']))
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']))
    assigned_to = fields.Int()
    created_by = fields.Int()
    search = fields.Str()

# Schema instances for reuse
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
case_create_schema = CaseCreateSchema()
case_update_schema = CaseUpdateSchema()
case_query_schema = CaseQuerySchema()