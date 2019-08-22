import vlibras_translate

class GTranslator():

	def __init__(self):
		try:
			self.tradutor = vlibras_translate.translation.Translation()
		except UnicodeDecodeError as ex:
			print(ex.encoding)
		
	def translate(self, text):
		translation = ""
		for line in text.splitlines():
			translation += self.tradutor.rule_translation(line)
			translation += '#_#'
		return translation
