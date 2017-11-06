from django.db import models
from sysauth.models import Customer

MONTHS = (
    (1,1),
    (2,2),
    (3,3),
    (4,4),
    (5,5),
    (6,6),
    (7,7),
    (8,8),
    (9,9),
    (10,10),
    (11,11),
    (12,12)
)

class WaterDeviceMixin:
    def last_collect_before(self,month,year):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        c = self.last_collect_at(month,year)
        return c if c is not None else self.last_collect_at(month,year)

    def last_collect_at(self,month,year):
        if year <= self.begin_year and month < self.begin_month:
            return None
        cs = self.collects.filter(month=month,year=year).order_by('-created_at')
        return cs[0] if cs.count() > 0 else None


    def value_at(self,month,year):
        if year <= self.begin_year and month < self.begin_month:
            return self.begin_value
        lc = self.last_collect(month,year)
        return lc.value if lc is not None else None

    def last_value(self):
        last_collect = self.collects.order_by('-created_at')
        return last_collect[0].value if len(last_collect) > 0 else self.begin_value

    def last_value_before(self,month,year):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        value = self.value_at(month,year)
        return value if value is not None else self.last_value_before(month,year)

    def used_at(self,month,year):
        value = self.value_at(month,year)
        last_value_before = self.last_value_before(month,year)
        return value - last_value_before if value is not None and last_value_before is not None else None


class DigitalWaterDevice(models.Model,WaterDeviceMixin):
    customer = models.ForeignKey(Customer,related_name='digital_water_devices')
    token = models.CharField(default='',max_length = 255)
    active = models.BooleanField(default=False)

    begin_value = models.IntegerField(default=0)

    begin_month = models.IntegerField(choices=MONTHS,default=1)
    begin_year = models.IntegerField(default=1)

    def __str__(self):
        return '"%s" [digital] of user "%s"' %(self.token, self.customer)
    def __unicode__(self):
        return self.__str__()



class MechanicsWaterDevice(models.Model,WaterDeviceMixin):
    customer = models.ForeignKey(Customer,related_name='mechanics_water_devices')
    token = models.CharField(default='',max_length = 255)
    active = models.BooleanField(default=False)

    begin_value = models.IntegerField(default=0)

    begin_month = models.IntegerField(choices=MONTHS,default=1)
    begin_year = models.IntegerField(default=1)

    def __str__(self):
        return '"%s" [mechanics] of user "%s"' %(self.token, self.customer)
    def __unicode__(self):
        return self.__str__()


class DigitalWaterDeviceCollect(models.Model):

    year = models.IntegerField(default=1)
    month = models.IntegerField(default=1,choices=MONTHS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    device = models.ForeignKey(DigitalWaterDevice,related_name='collects')
    value = models.IntegerField(default=0)

    def __str__(self):
        return 'month "%s", value "%s",device "%s"'% (self.month,self.value,self.device)
    def __unicode__(self):
        return self.__str__()


class MechanicsWaterDeviceCollect(models.Model):

    year = models.IntegerField(default=1)
    month = models.IntegerField(default=1,choices=MONTHS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    device = models.ForeignKey(MechanicsWaterDevice,related_name='collects')
    image = models.ImageField(upload_to='mechanics_water_device_collect_images',null=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return 'month "%s", value "%s",device "%s"'% (self.month,self.value,self.device)
    def __unicode__(self):
        return self.__str__()

class DigitalWaterDeviceUsed(models.Model):
    year = models.IntegerField(default=1)
    month = models.IntegerField(default=1,choices=MONTHS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    device = models.ForeignKey(DigitalWaterDevice,related_name='per_months')
    collect = models.ForeignKey(DigitalWaterDeviceCollect,related_name='collect_of',null=True)
    collect_before = models.ForeignKey(DigitalWaterDeviceCollect,related_name='collect_before_of',null=True)
    used = models.IntegerField(default=0)

    def __str__(self):
        return 'month "%s", used "%s",device "%s"'% (self.month,self.used,self.device)
    def __unicode__(self):
        return self.__str__()

class MechanicsWaterDeviceUsed(models.Model):
    year = models.IntegerField(default=1)
    month = models.IntegerField(default=1,choices=MONTHS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    device = models.ForeignKey(MechanicsWaterDevice,related_name='per_months')
    collect = models.ForeignKey(MechanicsWaterDeviceCollect,related_name='collect_of',null=True)
    collect_before = models.ForeignKey(MechanicsWaterDeviceCollect,related_name='collect_before_of',null=True)
    used = models.IntegerField(default=0,null=True)

    def __str__(self):
        return 'month "%s", used "%s",device "%s"'% (self.month,self.used,self.device)
    def __unicode__(self):
        return self.__str__()

class WaterBill(models.Model):
    year = models.IntegerField(default=1)
    month = models.IntegerField(default=1,choices=MONTHS)

    customer = models.ForeignKey(Customer,related_name='water_bills')

    digital_water_device_used = models.ForeignKey(DigitalWaterDeviceUsed,null=True)
    mechanics_water_device_used = models.ForeignKey(MechanicsWaterDeviceUsed,null=True)

    used = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    total = models.IntegerField(default=0)

    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-year','-month')

    def __str__(self):
        return '%s - %s, %s, used "%s", price "%s", total: "%s"' % (self.month,self.year,self.customer,self.used,self.price,self.total)
    def __unicode__(self):
        return self.__str__()


class IssueMessage(models.Model):
    customer = models.ForeignKey(Customer,related_name='issue_messages')
    title = models.CharField(max_length = 255)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '"%s", customer "%s", title "%s"' %(self.created_at,self.customer,self.title)
    def __unicode__(self):
        return self.__str__()

class AppRate(models.Model):
    RATES = (
        (1,1),
        (2,2),
        (3,3),
        (4,4),
        (5,5),
    )
    customer = models.OneToOneField(Customer,related_name='app_rate')
    rate = models.IntegerField(choices=RATES,default=5)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)

    def __str__(self):
        return '"%s" sao, "%s"' %( self.rate,self.message)
    def __unicode__(self):
        return self.__str__()
