import abc

class BaseSlice(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def getVersion(self, input):
		"""Get a version number as int"""
		return 0

	@abc.abstractmethod
	def extract(self, images):
		"""Extract features of the given images"""
		return None

