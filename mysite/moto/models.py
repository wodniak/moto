"""
    Declared models of application
"""

from django.db import models

#Parsed Motorcycles table
class CMotorcycles(models.Model):
    """
        moto info
    """
    idx = models.IntegerField(default=0)
    brand = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    desc = models.CharField(max_length=500)
    prodDate = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    motoType = models.CharField(max_length=200)
    mileage = models.IntegerField(default=0)
    engineCC = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        pretty_print = "ID: {}, Brand: {}, pub_date: {}".format(self.idx, self.brand, self.pub_date)
        return pretty_print
