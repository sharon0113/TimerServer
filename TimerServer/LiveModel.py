import MySQLdb
PORT = "http://121.41.85.39/"

import logging

fh = logging.FileHandler("test.log", "w")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh.setFormatter(formatter)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger('jobs')
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)

connection = MySQLdb.connect(host="121.41.85.39", port=3306, user="root", passwd="chaw5216", db="pptv" )

class liveModel(object):

	def __init__(self):
		super(liveModel, self).__init__()
		self.cursor = connection.cursor()

	def addLiveItem(self, name, date, url, state="live"):
		execute_String = "INSERT INTO m3u8live(name, `date`, category, state, url) VALUES(\'{0}\', \'{1}\', \'{2}\', \'{3}\', \'{4}\')".format(name, date, "liveSports", state, url)
		try:
			self.cursor.execute(execute_String)
		except Exception, e:
			logger.error(e)
			logger.error("501 write resource database error")
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
