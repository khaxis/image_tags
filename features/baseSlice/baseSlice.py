import abc

class BaseSlice(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def getVersion(self):
		"""Get a version number as int"""
		return 0

	@abc.abstractmethod
	def extract(self, images):
		"""Extract features of the given images"""
		return None

	@abc.abstractmethod
	def getName(self):
		"""Get name of the slice"""
		return None