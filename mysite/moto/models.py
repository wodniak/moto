"""
    Declared models of application
"""

from django.db import models


class CMotorcycles(models.Model):
    """
        Motorcycles table from project database
        It connects to the same base with pandas
    """
    index = models.IntegerField(blank=True, null=True)
    id = models.IntegerField(blank=True, primary_key=True)
    brand = models.TextField(blank=True, null=True)
    model = models.TextField(blank=True, null=True)
    # Field name made lowercase.
    proddate = models.IntegerField(db_column='prodDate', blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    # Field name made lowercase.
    mototype = models.TextField(db_column='motoType', blank=True, null=True)
    mileage = models.IntegerField(blank=True, null=True)
    # Field name made lowercase.
    enginecc = models.FloatField(db_column='engineCC', blank=True, null=True)
    desc = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'motorcycles'

    def __str__(self):
        pretty_print = "ID: {}, Brand: {}, pub_date: {}".format(
            self.id, self.brand, self.proddate)
        return pretty_print
