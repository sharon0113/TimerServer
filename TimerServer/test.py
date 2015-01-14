

def getLiveList(date):
	req = urllib2.Request("http://live.pptv.com/api/subject_list?cb=load.cbs.cbcb_4&date="+date+"&type=35&tid=&cid=&offset=0", headers={
		"user-agent": "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
		})
	try:
		webpage = urllib2.urlopen(req)
	except Exception, e:
		print e
		print "601 request fail in html page request"
	pageContent = webpage.read()
	
	#ORIGINAL URL LIST
	#href=\"http:\/\/v.pptv.com\/show\/Sv5GxS2TA0GkIoo.html
	regex = r"http:\\\/\\\/v.pptv\.com\\\/live\\\/[A-Za-z0-9]*\.html"
	pattern = re.compile(regex)
	matchGroup = pattern.findall(pageContent)

	urlNum = len(matchGroup)
	urlGroup = []
	for index in range(0, urlNum):
		urlGroup.append(matchGroup[index].replace("\\", ""))
	return urlGroup

print getBroadList("2015-01-14")