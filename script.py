from selenium import webdriver
from selenium.webdriver.edge.options import Options
import json
import csv


edge_options = Options()
edge_options.add_argument('--log-level=2')


class Parser:
	def __init__(self):
		self.spb = 'RU-SPE'
		self.msc = 'RU-MOW'
		self.offset = 0
		self.base_url = f'https://api.detmir.ru/v2/products?filter=categories[].alias:konstruktory;promo:false;withregion:{self.msc}&expand=meta.facet.ages.adults,meta.facet.gender.adults&meta=*&limit=30&offset={self.offset}&sort=popularity:desc'
		self.driver = webdriver.Edge()


	def get_full_count(self):
		url = self.base_url
		self.driver.get(url)
		data = self.driver.page_source.replace('</pre></body></html>', '')
		data = data.replace('<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', '')
		jsn = json.loads(data)
		return jsn['meta']['length']


	def get_json(self, url):
		self.driver.get(url)
		raw_jsn = self.driver.page_source[84:-20]
		jsn = json.loads(raw_jsn)['items']
		return jsn


	def write_to_csv(self, data):
		try:
			with open('tz.csv', 'a') as csvfile:
				writer = csv.writer(csvfile, delimiter=';')
				writer.writerow((
					data['id'], 
					data['title'], 
					data['price'], 
					data['city'], 
					data['promo_price'], 
					data['ref']))
		except Exception as e:
			print(e, data, sep='\n')


	def item_to_dict(self, item):
		city = []
		if self.msc in item['available']['offline']['region_iso_codes']:
			city.append('МСК')
		if self.spb in item['available']['offline']['region_iso_codes']:
			city.append('СПБ')
		D = {
			'id': item['id'],
			'title': item['title'],
			'city': ', '.join(city),
			'promo_price': str(item['price']['price']) + ' ' + item['price']['currency'],
			'ref': item['link']['web_url'],
			}
		try:
			D['price'] = str(item['old_price']['price']) + ' ' + item['old_price']['currency']
		except TypeError:
			D['price'] = ''
		return D


	def parse(self, doffset=30):
		max_count = self.get_full_count()
		for i in range(self.offset, max_count+doffset, doffset):
			url = f'https://api.detmir.ru/v2/products?filter=categories[].alias:konstruktory;promo:false;withregion:{self.msc}&expand=meta.facet.ages.adults,meta.facet.gender.adults&meta=*&limit=30&offset={self.offset}&sort=popularity:desc'
			data = self.get_json(url)
			for item in data:
				self.write_to_csv(self.item_to_dict(item))
			self.offset += doffset



if __name__ == '__main__':
	parser = Parser()
	parser.parse()