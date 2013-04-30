import cPickle as pickle
import os

if __name__ == "__main__":
	m = {}
	f = open('cameras', 'r')
	m = pickle.load(f)
	f.close()
	
	dir = 'camera_scores'
	filenames = os.listdir(dir)
	cameras = []
	for filename in filenames:
		f = open(os.path.join(dir, filename), 'r')
		cs = pickle.load(f)
		f.close()
		
		sorted_scores = sorted(cs.items(), key = lambda x: x[1], reverse = True)
		for key, value in sorted_scores[:15]:
			if not key in cameras:
				cameras.append(key)
			
	missing = []
	for c in cameras:
		if c in m:
			if 'price' in m[c]: 
				if m[c]['price'] == '$0.00':
					missing.append(c)
			else:
				missing.append(c)
		else:
			missing.append(c)
	
	print missing				
  	print 'Missing price', len(missing)
  	print 'Total', len(cameras)
  	
  	f1 = open('missing_price_cameras', 'wb')
  	f2 = open('fill_price_cameras', 'wb')
  	pickle.dump(cameras, f1)
  	
  	for c in missing:
	  	m[c]['price'] = '$' + raw_input(c + ': ')
		
	pickle.dump(m, f2)
	f1.close()
	f2.close()
	
	f = open('cameras', 'wb')
	pickle.dump(m,f)
	f.close()
	
	  	 