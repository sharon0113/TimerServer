import MySQLdb
import logging
from datetime import datetime
PORT = "http://121.41.85.39/"

logger = logging.getLogger('jobs')
logger.setLevel(logging.DEBUG)

class liveModel(object):

	def __init__(self):
		super(liveModel, self).__init__()
		connection = MySQLdb.connect(host="121.41.85.39", port=3306, user="root", passwd="chaw5216", db="pptv" )
		self.cursor = connection.cursor()

	def addLiveItem(self, name, date, url, state="live"):
		execute_String = "INSERT INTO m3u8live(name, `date`, category, state, url) VALUES(\'{0}\', \'{1}\', \'{2}\', \'{3}\', \'{4}\')".format(name, date, "liveSports", state, url)
		try:
			self.cursor.execute(execute_String)
		except Exception, e:
			logger.error(e)
			logger.error("501 write resource database error")
			return 0
		vid = self.cursor.lastrowid
		try:
			interface = PORT+"pptvlive/readlivem3u8"+str(vid)+".m3u?vid="+str(vid)
			execute_String = "UPDATE m3u8live SET interface = %s  WHERE vid = %s"
			self.cursor.execute(execute_String, (interface, vid))
		except Exception, e:
			logger.error(e)
			logger.error("503 url update error")
			vid = 0
		return vid

	def getVidByUrl(self, url):
		execute_String = "SELECT vid FROM m3u8live WHERE url = %s and `date`= %s"
		date = datetime.now().strftime("%Y-%m-%d")
		try:
			self.cursor.execute(execute_String, (url, date))
		except Exception, e:
			logger.error(e)
			logger.error("501 inquire vid by url error")
			return None
		info = self.cursor.fetchone()
		if info:
			vid = info[0]
		else:
			vid = None
		return vid

	def updateStateByUrl(self, url):
		execute_String = "UPDATE m3u8live SET  state = %s WHERE url = %s and `date`= %s"
		try:
			self.cursor.execute(execute_String, ("finish", url, date))
		except Exception, e:
			logger.error(e)
			logger.error("504 state update error")
			return "live"
		return "finish"
