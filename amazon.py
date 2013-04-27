from amazonproduct import API, AWSError
from fetch_camera_data import *
import cPickle as pickle

def lookup_price(searchTerm):
	AWS_KEY = 'AKIAIILUNE5IYH7BDF2A'
	SECRET_KEY = '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'
	ASSOC_TAG = 'camerarecomm-20'
	
	api = API(AWS_KEY, SECRET_KEY, 'us', ASSOC_TAG)
	price = -1
	title = ''
	
	try:
		results = api.item_search('Electronics', Keywords=searchTerm, 
								BrowseNode='281052', ResponseGroup='Large', ItemPage=1)
		if results is not None:
			for cam in results:
				try:
					#asin = cam.Items.Item.ASIN
					title = cam.Items.Item.ItemAttributes.Title.text
					price = cam.Items.Item.ItemAttributes.ListPrice.FormattedPrice.text
# 					print title, price
					break
				except:	
					price = -1
					title = ''

	except:
		print 'Item not found'
	
	return price, title
        		
if __name__ == "__main__":
	count = 0
	c = retrieve_data('camera')
	for camera in c.keys():
		print camera
		price, title = lookup_price(camera)
		if price > 0:
			c[camera]['price'] = price
			c[camera]['amazon_title'] = title
			print title, price
			count += 1
	
	print 'Total found', count
	
	f = open('cameras_with_price', 'wb')
	pickle.dump(c,f)
	f.close()