import requests
from lxml import html
import pymysql.cursors
from datetime import datetime

s = requests.Session()

connection = pymysql.connect(host='localhost',
							 user='root',
							 password='',
							 db='improvely',
							 charset='utf8mb4',
							 cursorclass=pymysql.cursors.DictCursor)


def exists(user_id):
	with connection.cursor() as cursor:
		sql = "SELECT * FROM person_details WHERE user_id = %s"
		cursor.execute(sql, (user_id))
		user = cursor.fetchone()
		if user:
			return True
		return False

def insert_data(visits, conversions, time_conversion, lifetime_value, user_id, time_ago):
	if exists(user_id):
		print("Updating {}".format(user_id))
		with connection.cursor() as cursor:
			sql = '''UPDATE person_details SET 
					conversions=%s, 
					visits=%s,
					lifetime_value=%s,
					time_conversions=%s,
					last_seen=%s 
				WHERE user_id =%s'''
			cursor.execute(sql, (conversions, visits, lifetime_value, time_conversion, time_ago, user_id))
		connection.commit()
	else:
		with connection.cursor() as cursor:
			sql = '''INSERT INTO person_details(conversions, visits, lifetime_value, user_id, time_conversions, last_seen) 
			VALUES(%s, %s, %s, %s, %s, %s)'''
			cursor.execute(sql, (conversions, visits, lifetime_value, user_id, time_conversion, time_ago))
	connection.commit()


def get_last_seen():
	with connection.cursor() as cursor:
		sql = "SELECT MAX(last_seen) as last_seen FROM person_details"
		cursor.execute(sql)
		timestamp = cursor.fetchone()
		if timestamp['last_seen']:
			return timestamp['last_seen']
		return False


def is_conversion(text):
	if 'Conversion' in text.strip().split():
		return True
	return False


def get_latest_activity(user_id):
	with connection.cursor() as cursor:
		sql = "SELECT MAX(timestamp) as timestamp FROM activity_timeline WHERE user_id = %s"
		cursor.execute(sql, (user_id,))
		timestamp = cursor.fetchone()
	if timestamp['timestamp']:
		return timestamp['timestamp']
	return False

def insert_conversion(user_id, revenue, reference, conversion_url, source, timestamp):
	with connection.cursor() as cursor:
		if reference is None:
			sql = '''INSERT INTO conversion (revenue, conversion_url, source)
			VALUES (%s, %s, %s)'''
			cursor.execute(sql, (revenue, conversion_url, source))
		else:
			sql = '''INSERT INTO conversion (revenue, reference, conversion_url, source)
			VALUES (%s, %s, %s, %s)'''
			cursor.execute(sql, (revenue, reference, conversion_url, source))
	connection.commit()
	with connection.cursor() as cursor:
		conversion_id = connection.insert_id()
		sql = '''INSERT INTO activity_timeline (user_id, activity_id, timestamp, activity_type_id)
		VALUES (%s, %s, %s, %s)'''
		cursor.execute(sql, (user_id, conversion_id, timestamp, 1))
	connection.commit()


def insert_ad(user_id, url_clicked, location, referrer, tracking_link, ad, location_ip, timestamp):
	with connection.cursor() as cursor:
		if referrer is None:
			sql = '''INSERT INTO ad_click (url_clicked, location, tracking_link, ad, location_ip)
			VALUES (%s, %s, %s, %s, %s)'''
			cursor.execute(sql, (url_clicked, location, tracking_link, ad, location_ip))
		else:
			sql = '''INSERT INTO ad_click (url_clicked, location, referrer, tracking_link, ad, location_ip)
			VALUES (%s, %s, %s, %s, %s, %s)'''
			cursor.execute(sql, (url_clicked, location, referrer, tracking_link, ad, location_ip))

	connection.commit()

	with connection.cursor() as cursor:
		ad_id = connection.insert_id()
		sql = '''INSERT INTO activity_timeline (user_id, activity_id, timestamp, activity_type_id)
		VALUES (%s, %s, %s, %s)'''
		cursor.execute(sql, (user_id, ad_id, timestamp, 2))
	connection.commit()
		

s.post('https://adrac.improvely.com/login', data={'from':'/login', 'email':'andy@primus.co.uk', 'password':'tgDrXvVRE8eywtj5'})
first_page = 'https://adrac.improvely.com/reports/ironmongeryonline/people/explore?page=1&filters[sort]=last_seen&filters[dir]=desc'
MAIN_URL = 'https://adrac.improvely.com'
last_seen = get_last_seen()




page = 1

def scrap_data(next_page=False, page=1):
	if not next_page:
		return None
	response = s.get(next_page)
	print(page)
	html_page = html.document_fromstring(response.content)
	tbody = html_page.xpath('//*[@id="report"]/tbody/tr')
	for tr in tbody:
		conversions = int(tr.xpath('td[4]/text()')[0].replace(',',''))
		lifetime_value = float(tr.xpath('td[5]/text()')[0].replace(',','').replace('£',''))
		# print(conversions, lifetime_value)
		time_ago = tr.xpath('//*[@id="report"]/tbody/tr[1]/td[8]/span/text()')[0]
		time_ago_py = datetime.strptime(time_ago, "%Y-%m-%d %H:%M:%S")
		if last_seen:
			if time_ago_py <= last_seen:
				return False
			if conversions > 0 or lifetime_value > 0.0:
				link = tr.xpath('td[2]/a')[0].attrib['href']
				info_html = s.get('{}{}'.format(MAIN_URL, link))
				info_page = html.document_fromstring(info_html.content)
				user_id = info_page.xpath('/html/body/div[3]/div[1]/div/div/h1/text()')[0]
				print(user_id)
				key_metrics = info_page.xpath('//div[@class="page-content key-metrics"]')[0]
				visits = int(key_metrics.xpath('div/div/b/text()')[0].replace(',',''))
				conversions_info = int(key_metrics.xpath('div/div[2]/b/text()')[0])
				time_to_conversion = int(key_metrics.xpath('div/div[3]/b/text()')[0].replace('Days', '').strip())
				lifetime_value_info = float(key_metrics.xpath('div/div[4]/b/text()')[0].replace('£',''))
				insert_data(visits, conversions_info, time_to_conversion, lifetime_value_info, user_id, time_ago)
				timeline = key_metrics.xpath('//*[@id="timeline"]/tbody/tr')
				latest_activity = get_latest_activity(user_id)
				for tr in timeline:
					timestamp = datetime.strptime(
							datetime.strptime(tr.xpath('td[2]/span/text()')[0], '%B %d, %Y %I:%M %p').strftime('%Y-%m-%d %H:%M:%S'),
							'%Y-%m-%d %H:%M:%S')
					if latest_activity:
						if timestamp <= latest_activity:
							continue
					if is_conversion(tr.xpath('td[2]/text()')[0]):
						try:
							revenue = float(tr.xpath('td[2]/table/tr[1]/td[3]/text()')[0].replace('£','').strip())
							reference = int(tr.xpath('td[2]/table/tr[2]/td[3]/text()')[0].strip())
							conversion_url = tr.xpath('td[2]/table/tr[3]/td[3]/a')[0].attrib['href']
							source = '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[4]/td[3]/a')[0].attrib['href'])
							insert_conversion(user_id, revenue, reference, conversion_url, source, timestamp)
						except:
							revenue = float(tr.xpath('td[2]/table/tr[1]/td[3]/text()')[0].replace('£','').strip())
							conversion_url = tr.xpath('td[2]/table/tr[2]/td[3]/a')[0].attrib['href']
							source = '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[3]/td[3]/a')[0].attrib['href'])
							insert_conversion(user_id, revenue, None, conversion_url, source, timestamp)
					else:
						try:
							link = tr.xpath('td[2]/a')[0].attrib['href']
							locations = tr.xpath('td[2]/table/tr[1]/td[3]/text()')[1].strip().split(' (')
							location = locations[0]
							location_ip = locations[1].strip(')')
							referrer =  tr.xpath('td[2]/table/tr[3]/td[3]/a')[0].attrib['href']
							tracking_link =  '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[3]/td[3]/a')[0].attrib['href'])
							ad = '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[4]/td[3]/a')[-1].attrib['href'])
							insert_ad(user_id, link, location, referrer, tracking_link, ad, location_ip, timestamp)
						except:
							link = tr.xpath('td[2]/a')[0].attrib['href']
							locations = tr.xpath('td[2]/table/tr[1]/td[3]/text()')[1].strip().split(' (')
							location = locations[0]
							location_ip = locations[1].strip(')')
							try:
								referrer =  '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[2]/td[3]/a')[0].attrib['href'])
							except:
								referrer = tr.xpath('td[2]/table/tr[2]/td[3]/text()')[0]
							ad = '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[3]/td[3]/a')[-1].attrib['href'])
							insert_ad(user_id, link, location, referrer, tracking_link, ad, location_ip, timestamp)
		else:
			if conversions > 0 or lifetime_value > 0.0:
				link = tr.xpath('td[2]/a')[0].attrib['href']
				info_html = s.get('{}{}'.format(MAIN_URL, link))
				info_page = html.document_fromstring(info_html.content)
				user_id = info_page.xpath('/html/body/div[3]/div[1]/div/div/h1/text()')[0]
				key_metrics = info_page.xpath('//div[@class="page-content key-metrics"]')[0]
				print(user_id)
				visits = int(key_metrics.xpath('div/div/b/text()')[0])
				conversions_info = int(key_metrics.xpath('div/div[2]/b/text()')[0])
				time_to_conversion = int(key_metrics.xpath('div/div[3]/b/text()')[0].replace('Days', '').strip())
				lifetime_value_info = float(key_metrics.xpath('div/div[4]/b/text()')[0].replace('£',''))
				insert_data(visits, conversions_info, time_to_conversion, lifetime_value_info, user_id, time_ago)
				timeline = key_metrics.xpath('//*[@id="timeline"]/tbody/tr')
				latest_activity = get_latest_activity(user_id)
				for tr in timeline:
					timestamp = datetime.strptime(
							datetime.strptime(tr.xpath('td[2]/span/text()')[0], '%B %d, %Y %I:%M %p').strftime('%Y-%m-%d %H:%M:%S'),
							'%Y-%m-%d %H:%M:%S')
					if latest_activity:
						if timestamp <= latest_activity:
							continue
					if is_conversion(tr.xpath('td[2]/text()')[0]):
						try:
							revenue = float(tr.xpath('td[2]/table/tr[1]/td[3]/text()')[0].replace('£','').strip())
							reference = int(tr.xpath('td[2]/table/tr[2]/td[3]/text()')[0].strip())
							conversion_url = tr.xpath('td[2]/table/tr[3]/td[3]/a')[0].attrib['href']
							source = '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[4]/td[3]/a')[0].attrib['href'])
							insert_conversion(user_id, revenue, reference, conversion_url, source, timestamp)
						except:
							revenue = float(tr.xpath('td[2]/table/tr[1]/td[3]/text()')[0].replace('£','').strip())
							conversion_url = tr.xpath('td[2]/table/tr[2]/td[3]/a')[0].attrib['href']
							source = '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[3]/td[3]/a')[0].attrib['href'])
							insert_conversion(user_id, revenue, None, conversion_url, source, timestamp)
					else:
						try:
							link = tr.xpath('td[2]/a')[0].attrib['href']
							locations = tr.xpath('td[2]/table/tr[1]/td[3]/text()')[1].strip().split(' (')
							location = locations[0]
							location_ip = locations[1].strip(')')
							referrer =  tr.xpath('td[2]/table/tr[3]/td[3]/a')[0].attrib['href']
							tracking_link =  '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[3]/td[3]/a')[0].attrib['href'])
							ad = '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[4]/td[3]/a')[-1].attrib['href'])
							insert_ad(user_id, link, location, referrer, tracking_link, ad, location_ip, timestamp)
						except:
							link = tr.xpath('td[2]/a')[0].attrib['href']
							locations = tr.xpath('td[2]/table/tr[1]/td[3]/text()')[1].strip().split(' (')
							location = locations[0]
							location_ip = locations[1].strip(')')
							try:
								referrer =  '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[2]/td[3]/a')[0].attrib['href'])
							except:
								referrer = tr.xpath('td[2]/table/tr[2]/td[3]/text()')[0]
							ad = '{}{}'.format(MAIN_URL, tr.xpath('td[2]/table/tr[3]/td[3]/a')[-1].attrib['href'])
							insert_ad(user_id, link, location, referrer, tracking_link, ad, location_ip, timestamp)
						

	next_page = html_page.xpath('/html/body/div[3]/div[2]/div/div/div[1]/a[2]')[0]
	page += 1
	if 'disabled' in next_page.attrib:
		return scrap_data()
	return scrap_data(next_page='{}{}'.format(MAIN_URL, next_page.attrib['href']), page=page)

if not scrap_data(next_page=first_page):
	print("Everything has been scrapped already!")
connection.close()
