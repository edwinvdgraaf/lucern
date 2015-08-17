# inspired by https://docs.djangoproject.com/en/1.8/_modules/django/utils/text/#slugify
def slugify(value):
  """
  Converts to ASCII. Converts spaces to hyphens. Removes characters that
  aren't alphanumerics, underscores, or hyphens. Converts to lowercase.
  Also strips leading and trailing whitespace.
  """
  # value = force_text(value)
  import unicodedata, re
  value = re.sub('/', '-', value).strip().lower()
  value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
  value = re.sub('[^\w\s-]', '', value).strip().lower()
  return re.sub('[-\s]+', '-', value)
