import MySQLdb
PORT = "http://127.0.0.1/"

connection = MySQLdb.connect(host="127.0.0.1", port=3306, user="root", passwd="", db="resource" )

class liveModel(object):

	def __init__(self):
		super(liveModel, self).__init__()
		self.cursor = connection.cursor()

	def addLiveItem(self, name, date, url, state="live"):
		execute_String = "INSERT INTO m3u8live(name, `date`, category, state, url) VALUES(\'{0}\', \'{1}\', \'{2}\', \'{3}\', \'{4}\')".format(name, date, "liveSports", state, url)
		try:
			self.cursor.execute(execute_String)
		except Exception, e:
			print e
			print "501 write resource database error"
		vid = self.cursor.lastrowid
		try:
			interface = PORT+"read_m3u8_live"+str(vid)+".m3u?vid="+str(vid)
			execute_String = "UPDATE m3u8live SET interface = %s  WHERE vid = %s"
			self.cursor.execute(execute_String, (interface, vid))
		except Exception, e:
			print e
			print "501 url update error"
			vid = 0
