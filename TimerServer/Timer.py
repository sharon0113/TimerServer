# -*- coding: utf-8 -*-

from datetime import datetime
from Downloader import M3u8LiveDownloader
from LiveModel import liveModel
import urllib2
from time import sleep
from daemonize import Daemonize
import re
import logging

fh = logging.FileHandler("test.log", "w")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh.setFormatter(formatter)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger('jobs')
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)

PORT = "http://121.41.85.39/"
ROOT = "/mnt/m3u8/"
INTERSECTION = 60

InfoList = {}

def getLiveList(date):
	req = urllib2.Request("http://live.pptv.com/api/subject_list?cb=load.cbs.cbcb_4&date="+date+"&type=35&tid=&cid=&offset=0", headers={
		"user-agent": "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
		})
	try:
		webpage = urllib2.urlopen(req)
	except Exception, e:
		logger.error(e)
		logger.error("601 request fail in html page request")
		return []

	pageContent = webpage.read().replace(" ","#").replace("\\", "")
	
	#ORIGINAL URL LIST
	afcPattern = re.compile(r"\"(http:\/\/[a-zA-Z0-9]*\.pptv\.com\/[a-zA-Z0-9\/]*\.html)\"###title=\"u76f4u64adu4e2d")
	afcList = afcPattern.findall(pageContent)
	cbaPattern = re.compile(r"(http:\/\/[a-zA-Z0-9]*\.pptv\.com\/live[0-9]*)\/\"###title=\"u76f4u64adu4e2d\"")
	cbaList = cbaPattern.findall(pageContent)
	matchGroup = cbaList + afcList

	urlNum = len(matchGroup)
	urlGroup = []
	for index in range(0, urlNum):
		urlGroup.append(matchGroup[index].replace("\\", ""))
	return urlGroup


def runTimer():
	currentDate = "2015-01-14"
	while(True):
		logger.debug("run it in "+datetime.now().strftime("%T"))
		starttime = datetime.now()
		lastDate = currentDate
		currentDate = datetime.now().strftime("%Y-%m-%d")
		currentTime = datetime.now().strftime("%H:%M")
		#part only newday execute
		if currentDate != lastDate:
			InfoList = {}
			logger.debug("new day "+ currentDate + " started")
		#part every loop to examine
		liveList = getLiveList(currentDate)
		logger.debug(liveList)
		if liveList:
			logger.debug(str(len(liveList))+" live urls fetched...")
		else:
			logger.debug("No lives...")
		currentInfolist = {}
		for liveUrl in liveList:
			if liveUrl in InfoList.keys():
				currentInfolist[liveUrl] = InfoList[liveUrl]
				vid = liveModel().getVidByUrl(liveUrl)
				currentSet = M3u8LiveDownloader(liveUrl, currentInfolist[liveUrl], vid).runDownloader()
			else:
				currentInfolist[liveUrl] = set([])
				InfoList[liveUrl] = currentInfolist[liveUrl]
				currentSet = M3u8LiveDownloader(liveUrl, currentInfolist[liveUrl], None).runDownloader()
			if currentSet["state"] == True:
				InfoList[liveUrl] = currentSet["downloadSet"]
			else:
				InfoList[liveUrl] = set([])
		endtime = datetime.now()
		delta = (endtime - starttime).total_seconds()
		delta = int(delta)
		if delta < INTERSECTION:
			logger.debug("Server sleeps...")
			remains = INTERSECTION - delta
			sleep(remains)
		else:
			logger.debug("WARNING: while loop runs over 2 seconds.")


if __name__=='__main__':
	pid="timer.pid"
	
	keep_fds = [fh.stream.fileno()]
	# servermain()
	daemon = Daemonize(app="jobs", pid=pid, action=runTimer,keep_fds=keep_fds)
	daemon.start()
	#runTimer()





	






 
