from django.db import models

from contingent.models import DictCitizen


class AddressType(models.Model):
    short_type = models.CharField('Сокращенный тип', max_length=10)
    type = models.CharField('Полный тип', max_length=100)

    def __str__(self):
        return self.short_type

    class Meta:
        abstract = True


class RegionType(AddressType):
    pass


class SettlementType(AddressType):
    pass


class StreetType(AddressType):
    pass


class Address(models.Model):
    country = models.ForeignKey(DictCitizen, verbose_name='Страна', on_delete=models.CASCADE, null=True, blank=True)
    region = models.CharField('Регион', max_length=500, null=True, blank=True)
    region_type = models.ForeignKey(RegionType, verbose_name='Тип региона', on_delete=models.CASCADE, null=True,
                                    blank=True)
    district = models.CharField('Район', max_length=500, null=True, blank=True)
    settlement = models.CharField('Поселок', max_length=500, null=True, blank=True)
    settlement_type = models.ForeignKey(SettlementType, verbose_name='Тип населенного пункта', on_delete=models.CASCADE,
                                        null=True, blank=True)
    street = models.CharField('Улица', max_length=500, null=True, blank=True)
    street_type = models.ForeignKey(StreetType, verbose_name='Тип улицы', on_delete=models.CASCADE, null=True,
                                    blank=True)
    building = models.CharField(max_length=100, verbose_name='Номер дома', null=True, blank=True)
    flat = models.CharField(max_length=100, verbose_name='Номер квартиры', null=True, blank=True)

    index = models.CharField(max_length=16, verbose_name='Почтовый индекс', null=True, blank=True)

    # id в кладр уровня дома или улицы
    kladr_id = models.CharField(max_length=100, verbose_name='Код КЛАДР', null=True, blank=True)
    # уникальный идентификатор фиас
    fias_unid = models.CharField(max_length=500, verbose_name='Код ФИАС', null=True, blank=True)

    def get_json(self):
        addr = {}
        if self.index:
            addr['index'] = self.index
        if self.country:
            addr['country'] = str(self.country)
        if self.region:
            addr['region'] = self.region + ' ' + str(self.region_type)
        if self.district:
            addr['district'] = self.district + ' р-н'
        if self.settlement:
            addr['settlement'] = self.settlement + ' ' + str(self.settlement_type)
        if self.street:
            addr['street'] = self.street + ' ' + str(self.street_type)
        if self.building:
            addr['building'] = self.building
        if self.flat:
            addr['flat'] = self.flat

    def __str__(self):
        addr = ''
        if self.index:
            addr += self.index + ', '
        if self.country:
            addr += str(self.country) + ', '
        if self.region:
            addr += self.region + ' ' + str(self.region_type) + ', '
        if self.district:
            addr += self.district + ' р-н, '
        if self.settlement:
            addr += self.settlement + ' ' + str(self.settlement_type) + ', '
        if self.street:
            addr += self.street + ' ' + str(self.street_type) + ', '
        if self.building:
            addr += str(self.building) + ' дом, '
        if self.flat:
            addr += str(self.flat) + ' кв.'
        return addr.strip(', ')
