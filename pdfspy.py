"""Tracks Changes over days for a collection of PDFs on an index page"""

import sys,urllib2,re,httplib,os,time

#today's date
d = int(time.time())

#validate arguments
try:
	url = sys.argv[1]
	c_path = sys.argv[2]
except:
	print("Usage:  pdfr.py [options] URL collectn-path")
	sys.exit()

#prepare a root url in case of relative linking in the document
url_root = '/'.join(url.split('/')[:-1]) + '/' #todo use this 

#init path args
c_pdf_path = c_path + 'pdf/'

#open the source file
f = urllib2.urlopen(url)
index_page = f.read()
f.close()

#now validate the colletion path. create a new one if necessary

#does the collection exist?
if not os.path.exists(c_path):
	os.mkdir(c_path)
	os.mkdir(c_pdf_path)

#find all the pdf links on it
pattern = 'http:\/\/.*?\.pdf' #todo generalize this so that relative links are matched
matches = list(set(re.findall(pattern,index_page)))

#process the pdf links
for match in matches:
	
	parts = match.split('/')
	filename = parts[-1]
	filename_noextn = filename.replace('.pdf','')
	files_path = c_pdf_path + filename_noextn + '/'
	
	#no path for this file?  make one!
	if not os.path.exists(files_path):
		os.mkdir(files_path)
		os.mkdir(files_path + str(d))
		# so we know that we want to save the pdf
		try:
			u = urllib2.urlopen(match)
		except:
			continue
		
		date_path = files_path + str(d) + '/'
		
		f = open(date_path + filename,'wb')
		f.write(u.read())
		f.close()
		
		meta = u.headers['Content-Length'] + '|' + u.headers['Last-Modified']
		
		f2 = open(date_path + '.meta','w')
		f2.write(meta)
		f2.close()
		
		print("Detected and cached new file " + filename)
	
	else:
		# the directory already exists, so let's check for a change
		
		#what's the most recent file's path?
		ls = os.listdir(files_path)
		ls.sort()
		d_recent = ls[0]
		
		date_path = files_path + d_recent + '/'
		
		#get basic facts about the most recent local file from the .meta file
		local = date_path + filename 
		f = open(date_path + '.meta','r')
		tmp = f.read(); meta = tmp.split('|')
		local_size,local_mod_date = meta[0],meta[1]
		
		#now get analogous facts about the external file
		external = urllib2.urlopen(match)
		external_size,external_mod_date = external.headers["Content-Length"],external.headers["Last-Modified"]
		
		#print('L: ',local_size,' ',local_mod_date,'E: ',external_size,' ',external_mod_date)
		#sys.exit()
		if ((local_mod_date.strip(' \t\n\r')!=external_mod_date.strip(' \t\n\r')) or (local_size.strip(' \t\n\r')!=external_size.strip(' \t\n\r'))):
			
			#there's a change -- write a new file
			date_path = files_path + str(d) + '/'
			os.mkdir(date_path)
			f = open(date_path + filename,'wb')
			f.write(external.read())
			f.close()
			
			meta = external_size + '|' + external_mod_date
			
			#now write the meta file
			f2 = open(date_path + '.meta','w')
			f2.write(meta)
			f2.close()
			
						
			print("Detected changed file " + filename)	
		

print("done")
