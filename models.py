from tortoise import fields, models

class Router(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    ip = fields.CharField(max_length=100, unique=True)
    snmp_user = fields.CharField(max_length=100)
    snmp_pass = fields.CharField(max_length=100)

    class Meta:
        table = "router"