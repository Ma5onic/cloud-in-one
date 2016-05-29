import os.path
from cmd import Cmd
from log import Logger

class Repl(Cmd):
    """
    Read-Execute-Print Loop to interact with the application
	Acts as a Command Line Interface for the application
    """
    def __init__(self, manager):
    	Cmd.__init__(self)
    	self.logger = Logger(__name__)
    	self.manager = manager

    def do_s(self,arg):
    	self.do_sync(arg)

    def do_sync(self, arg):
    	"""Force the synchronization process"""
    	self.manager.updateLocalSyncFolder()

    def do_download(self, arg):
    	"""Download a single file"""
    	self.logger.debug(arg)
    	self.logger.debug(type(arg))
    	self._downloadFile()

    # TODO: Move to somewhere logical, not here! And check values correctly
    def _downloadFile(self):
        walkedFiles = self.manager.walkRemoteFiles()
        paths = [d['path'] for d in walkedFiles]
        accounts = [d['account'] for d in walkedFiles]
        for i, path in enumerate(paths, 1):
            print(i, path)

        selected = int(input("Select a file (0 to cancel): ")) - 1
        if selected == -1:
            return
        elif selected < len(paths):
            print("Downloading <" + paths[selected] + ">")
            self.manager.donwloadFile(accounts[selected], paths[selected])

    def do_q(self, arg):
    	return self.do_quit(arg)

    def do_quit(self, arg):
    	return True

    def start(self):
    	self.cmdloop("Cloud-In-One")

