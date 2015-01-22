# -*- coding: utf-8 -*-
 
import logging
import urllib2
from datetime import datetime
from BeautifulSoup import BeautifulSoup
import os
import re
from LiveModel import liveModel
from utils import ROOT, PORT, M3U8PATH, M3U8SUBPATH, M3U8NEWPATH, TSPATH


date = datetime.now().strftime("%Y-%m-%d")

logger = logging.getLogger('jobs')
logger.setLevel(logging.DEBUG)

# def urlDownloader(url, tsCode, vid):
# 	trialCount = 0
# 	state = False
# 	while state==False and trialCount <5:
# 		state = downloadByUrl(url, tsCode, vid)
# 	return state

def urlDownloader(url, tsCode, vid):
	request = urllib2.Request(url, headers={
		"user-agent": "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
		})
	logger.debug("Downloading "+url)
	logger.debug("###########DEBUG###########")
	logger.debug("downloading video"+str(vid)+"-"+str(tsCode)+"start at: "+datetime.now().strftime("%T"))
	try:
		tsPage = urllib2.urlopen(request, timeout=5)
		tsContent = tsPage.read()
	except Exception, e:
		logger.debug(e)
		logger.debug("205 "+str(vid)+"-"+str(tsCode)+"time out for 1st")
		try:
			tsPage = urllib2.urlopen(request, timeout=5)
			tsContent = tsPage.read()
		except Exception, e:
			logger.debug(e)
			logger.debug("205 "+str(vid)+"-"+str(tsCode)+"time out for 2nd")
				# try:
				# 	tsPage = urllib2.urlopen(request, timeout=3)
				# 	tsContent = tsPage.read()
				# except Exception, e:
				# 	logger.debug(e)
				# 	logger.debug("205 "+str(vid)+"-"+str(tsCode)+"time out for 3rd")
			return True
	logger.debug("end video"+str(vid)+"-"+str(tsCode)+"at: "+datetime.now().strftime("%T")+", successful")
	logger.debug("###########DEBUG###########")
	fp = open(TSPATH+date+"-"+str(vid)+"-"+tsCode+".ts", "w")
	fp.write(tsContent)
	fp.close()
	return True

class M3u8LiveDownloader(object):

	def __init__(self, url, downloadSet, vid):
		super(M3u8LiveDownloader, self).__init__()
		date = datetime.now().strftime("%Y-%m-%d")
		if vid==None:
			self.isFirstTime = True
		else:
			self.isFirstTime = False
		self.vid = vid
		self.liveUrl = url
		request = urllib2.Request(self.liveUrl, headers={
			"user-agent": "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
			})
		webPage = urllib2.urlopen(request)
		pageContent = webPage.read()
		pageContent=pageContent.replace(" ", "").replace("\t", "").replace("\n", "")
		#http://web-play.pptv.com/web-m3u8-300617.m3u8?type=m3u8.web.pad;playback=0;kk=;o=leader.pptv.com;rcc_id=0
		regex = r"<scripttype=\"text/javascript\">varwebcfg={.*};</script>"
		pattern = re.compile(regex)
		matcher = pattern.search(pageContent)
		if matcher:
			soup = BeautifulSoup(matcher.group())
			webcfg = matcher.group().replace(" ", "").replace("\t", "").replace("\n", "")
			idPattern = re.compile(r"\"id\":[0-9]*")
			idValue = idPattern.search(webcfg).group()
			idValue = idValue.split(":")[1]
			kkPattern = re.compile(r"\"ctx\":\"[A-Za-z0-9%]*%3D[A-Za-z0-9-]*\"")
			kkValue = kkPattern.search(webcfg).group()
			kkValueGroup=kkValue.split("3D")
			kkValue = kkValueGroup[len(kkValueGroup)-1].strip("\"")
			self.m3u8Url = "http://web-play.pptv.com/web-m3u8-"+idValue+".m3u8?type=m3u8.web.pad&playback=0&kk="+kkValue+"&o=v.pptv.com&rcc_id=0"
		else:
			regex = r"videoPlayer\.play\(\'([0-9]*)\'"
			pattern = re.compile(regex)
			matcher = pattern.findall(pageContent)
			if matcher:
				idValue = matcher[0]
				self.m3u8Url = "http://web-play.pptv.com/web-m3u8-"+idValue+".m3u8?type=m3u8.web.pad&playback=0&kk=&o=leader.pptv.com&rcc_id=0"
			else:
				logger.debug("NOT MATCHED")
				self.m3u8Url = "urlNotExisted"
		logger.debug(str(self.m3u8Url)+"downloaded")
		self.name = u"Live Channel"
		if vid==None:
			vid = liveModel().addLiveItem(self.name, date, self.liveUrl)
			self.vid = vid
		self.tsDownloadSet = downloadSet

	def runDownloader(self):
		logger.debug("Downloader initializing...")
		if self.m3u8Url == "urlNotExisted":
			return {"state":False, "downloadSet":self.tsDownloadSet}
		request = urllib2.Request(self.m3u8Url, headers={
			"user-agent": "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
			})
		m3u8Page = urllib2.urlopen(request)
		m3u8Content = m3u8Page.read()
		logger.debug("Downloading m3u8 level 1...")
		fp = open(M3U8PATH+date+"-"+str(self.vid)+".m3u", "w")
		fp.write(m3u8Content)
		fp.close()
		m3u8SubPattern = re.compile(r"http://[0-9.:]*/live/[0-9\/]*/[a-zA-Z0-9]*\.m3u8\?playback=[0-9]*&rcc_id=[0-9]*&pre=[a-zA-Z0-9]*&o=[a-z]*\.pptv\.com&type=m3u8\.web\.pad&kk=[a-zA-Z0-9-]*&chid=[0-9]*&k=[a-zA-Z0-9-%_]*")
		m3u8SubList = m3u8SubPattern.findall(m3u8Content)
		#logger.debug(str(len(m3u8SubList)) + " m3u8 urls successfully fetched, start downloading first m3u8 level 2 file...")
		tempContent = """#EXTM3U\n#EXT-X-TARGETDURATION:5\n#EXT-X-VERSION:3\n#EXT-X-MEDIA-SEQUENCE:"""
		tsCount = 0
		if m3u8SubList:
			m3u8SubUrl = m3u8SubList[0]
			try:
				portPattern = re.compile(r"[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*:[0-9]*")
				matcher = portPattern.search(m3u8SubUrl)
				if matcher:
					ipAddress = matcher.group()
					ipCode = ipAddress.replace(":","").replace(".","")
				else:
					ipAddress = "0.0.0.0:80"
					ipCode = "000080"
				currentRequest = urllib2.Request(m3u8SubUrl, headers={
				"user-agent": "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
				})
				m3u8SubPage = urllib2.urlopen(currentRequest)
				m3u8SubContent = m3u8SubPage.read()
				fp = open(M3U8SUBPATH+date+"-"+str(self.vid)+"-"+ipCode+".m3u", "w")
				fp.write(m3u8SubContent)
				fp.close()
				tsPattern = re.compile(r"/live/[a-zA-Z0-9]*/[0-9]*.ts\?pre=ikan&o=[a-z]*.pptv.com&playback=[0-9]*&k=[a-zA-Z0-9-]*&segment=[a-zA-Z0-9_]*&type=m3u8\.web\.pad&chid=[0-9]*&kk=[a-zA-Z0-9-]*&rcc_id=[0-9]*")
				tsList = tsPattern.findall(m3u8SubContent)
				logger.debug("m3u8 level 2 successfully downloaded, "+str(len(tsList))+" ts files in total")
				serialPattern = re.compile(r"#EXT-X-MEDIA-SEQUENCE:([0-9]*)")
				matcher = serialPattern.findall(m3u8SubContent)
				if matcher:
					serialCode = str(matcher[0])
				else:
					serialCode = "284222306"
				# tempPointer = open(M3U8NEWPATH+date+"-"+str(self.vid)+".m3u", "a+") 
				# tempPointer.seek(0,2)
				tempContent = tempContent + str(serialCode) + "\n"
				threadPool = []
				# logger.debug("##########MULTITHREAD#########")
				logger.debug("start multithread at: "+datetime.now().strftime("%T"))
				urlCount = 0
				for tsUrl in tsList:
					urlCount += 1
					url = "http://"+ ipAddress+ tsUrl
					codePattern = re.compile(r"[0-9]*\.ts")
					matcher = codePattern.search(tsUrl)
					if matcher:
						tsCode = matcher.group().replace(".ts", "")
					else:
						tsCode = "00000X"
					if self.isFirstTime:
						if urlCount > 360:
							state = urlDownloader(url, tsCode, self.vid)
							self.tsDownloadSet.add(tsCode)
						else:
							self.tsDownloadSet.add(tsCode)
							state = True
					else:
						if tsCode not in self.tsDownloadSet and tsCode != "00000X":
							# currentThread = MyThread(urlDownloader, (url, tsCode, self.vid), str(self.vid))
							# threadPool.append(currentThread)
							state = urlDownloader(url, tsCode, self.vid)
							self.tsDownloadSet.add(tsCode)
						else:
							state = True
							# logger.debug(str(tsCode) +"already downloaded, pass it")
					if state:
						tempContent = tempContent + "#EXTINF:5,\n"+PORT+"pptvlive/readlivets"+"_"+str(self.vid)+"_"+tsCode+".ts?tsCode="+tsCode+"&vid="+str(self.vid)+"\n"
					# tempPointer = open(M3U8NEWPATH+date+"-"+str(self.vid)+".m3u", "a+") 
					# tempPointer.seek(0,2)
				logger.debug("end multithread at: "+datetime.now().strftime("%T"))
				# logger.debug("##########MULTITHREAD#########")
			except Exception,e:
				logger.error(e)
				logger.error("202 sub m3u9 process error, try another one.")
				return {"state":False, "downloadSet":self.tsDownloadSet}
		else:
			return {"state":False, "downloadSet":self.tsDownloadSet}
		logger.debug("###########DEBUG###########")		
		logger.debug("rewrite video  "+str(self.vid)+"  at: "+datetime.now().strftime("%T"))
		resultPointer = open(M3U8NEWPATH+date+"-"+str(self.vid)+".m3u", "w")
		resultPointer.write(tempContent)
		resultPointer.close()
		logger.debug("end rewrite video  "+str(self.vid)+"  at: "+datetime.now().strftime("%T"))
		logger.debug("Congratulations, download finished")
		logger.debug("###########DEBUG###########")
		return {"state":True, "downloadSet":self.tsDownloadSet}

