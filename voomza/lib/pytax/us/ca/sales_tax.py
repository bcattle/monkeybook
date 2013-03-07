from __future__ import division, print_function, unicode_literals
import logging, csv, decimal

logger = logging.getLogger(__name__)


class InvalidZIPCodeError(Exception):
    pass

class CityNotFoundError(Exception):
    pass

class CASalesTaxCalculator(object):
    default_rate = decimal.Decimal('7.5')

    def __init__(self):
        with open('CA_zip_codes.csv') as zip_codes_file:
            with open('2013_City_Rates.csv') as city_rates_file:
                zip_codes_reader = csv.DictReader(zip_codes_file)
                city_rates_reader = csv.DictReader(city_rates_file)

                self.cities_by_zip_code = { int(x['Zip Code']): (x['City'], x['County'],)
                                            for x in zip_codes_reader }

                self.rates_by_city = { (x['City'], x['County'],): x['Rate']
                                       for x in city_rates_reader }

    def get_sales_tax_rate_from_zip(self, zip_code):
        try:
            city_county = self.cities_by_zip_code[zip_code]
        except KeyError:
            raise InvalidZIPCodeError
        try:
            rate = self.rates_by_city[city_county]
        except KeyError:
            raise CityNotFoundError
        return decimal.Decimal(rate)

    def get_city_from_zip(self, zip_code):
        return self.cities_by_zip_code[zip_code][0]

