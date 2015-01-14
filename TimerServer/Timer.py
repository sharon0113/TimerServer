from datetime import datetime
from Downloader import M3u8LiveDownloader
import urllib2
from time import sleep
from daemonize import Daemonize
import re

PORT = "http://127.0.0.1:8000/"
ROOT = "/mnt/m3u8/"
INTERSECTION = 120

startDate = "2015-01-13"
InfoList = {}

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


def runTimer(startDate):
	currentDate = startDate
	while(True):
		print "run it in "+datetime.now().strftime("%T")
		starttime = datetime.now()
		lastDate = currentDate
		currentDate = datetime.now().strftime("%Y-%m-%d")
		currentTime = datetime.now().strftime("%H:%M")
		#part only newday execute
		if currentDate != lastDate:
			print "new day "+ currentDate + " started"
		#part every loop to examine
		liveList = getLiveList(currentDate)
		if liveList:
			print str(len(livelist))+" live urls fetched..."
		else:
			print "No lives..."
		currentInfolist = {}
		for liveUrl in liveList:
			if liveUrl in InfoList.keys():
				currentInfolist[liveUrl] = InfoList[liveUrl]
			else:
				currentInfolist[liveUrl] = set([])
				InfoList[liveUrl] = currentInfolist[liveUrl]
			currentSet = M3u8LiveDownloader(liveUrl, currentInfolist[liveUrl]).runDownloader()
			InfoList[liveUrl] = currentSet
		endtime = datetime.now()
		delta = (endtime - starttime).total_seconds()
		delta = int(delta)
		if delta < INTERSECTION:
			print "Server sleeps..."
			remains = INTERSECTION - delta
			sleep(remains)
		else:
			print "WARNING: while loop runs over 2 seconds."

# if __name__=='__main__':
# 	pid="timer.pid"
	
# 	# keep_fds = [fh.stream.fileno()]
# 	# servermain()
# 	daemon = Daemonize(app="jobs", pid=pid, action=runTimer,keep_fds=None)
# 	daemon.start()
	
runTimer(startDate)	



	







	






 