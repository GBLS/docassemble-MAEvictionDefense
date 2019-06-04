# coding=utf-8
from docassemble.base.functions import url_action
from six import text_type

def get_tuples(lang_codes):
  """ Returns a list of tuples representing the language name, followed by language ISO 639-1 code.
  Right now only lists languages in use by Massachusetts Defense for Eviction (MADE)."""
  long_langs = {'en': 'English',
   'es': u'Español',
   'vn': u'Tiếng Việt',
   'ht': u'Kreyòl',
   'zh': u'中文',
   'pt': u'Português'
  }
  tuples = []
  for lang in lang_codes:
    tuples.append((long_langs[lang],lang))
  return tuples    
  

def get_language_list(languages, current=''):
  """ given a list of ordered tuples with (Description, language_code), returns
    an Bootstrap-formatted unordered inline list. The current language will not be a link."""
  list_start = '<ul class="list-inline">'
  list_start += '<li class="list-inline-item"><b>Language</b>:</li>'
  list_end = '</ul>'
  for language in languages:
    if language[1] == current:
      list_start += get_language_list_item(language, link=False)
    else:
      list_start += get_language_list_item(language)
  return list_start + list_end      

def get_language_list_item(language, link=True):
  """ Given an ordered tuple, returns a link to the current interview with lang=language code and the link title
    given in the first part of the tuple."""
  li_start = '<li class="list-inline-item">'
  li_end = '</li>'
  
  if link:
    iurl = url_action('change_language', lang = language[1])
    return li_start + '<a target="_self" href="' + iurl + '">' + language[0] + '</a>' + li_end
  else:
    return li_start + language[0] + li_end     