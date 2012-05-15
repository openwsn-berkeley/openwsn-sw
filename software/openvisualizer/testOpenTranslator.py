from openTranslator import openTranslator

testClass = openTranslator()

for comp in testClass.componentIdentifiers:
   for error in testClass.errorCodes:
      errorString, seriousness = testClass.translateErrortoString(0,comp,error,12,34)
      print errorString