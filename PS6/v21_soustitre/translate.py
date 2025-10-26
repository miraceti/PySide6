from deep_translator import GoogleTranslator
translated = GoogleTranslator(source='auto',target='fr').translate("we make for the Elven Tower at first light.")
print(translated)