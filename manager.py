class Manager():
	"""Manager of the Cloud-In-One application.
	It is responsible for the control flow and coordination of components"""
	def __init__(self, user, password):
		self.user = user
		self.password = password
		self.cuentas = []
		#TODO: inicializar los módulos de seguridad y FS
		self.securityModule = None
		self.fileSystemModule = None

	def newAccount(self,type,user):
		# Do whatever it's needed to add a new account
		return True

	def deleteAccount(self,account):
		# Do things to delete an account
		return True
	

		