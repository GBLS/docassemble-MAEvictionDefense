# coding=utf-8
from docassemble.base.functions import url_action

def get_tuples(lang_codes):
  """ Returns a list of tuples representing the language name, followed by language ISO 639-1 code.
  Right now only lists languages in use by Massachusetts Defense for Eviction (MADE)."""
  long_langs = {'en': 'English',
   'es': u'Español',
   'vi': u'Tiếng Việt',
   'ht': u'Kreyòl',
   'zh-t': u'中文',
   'pt': u'Português'
  }
  tuples = []
  for lang in lang_codes:
    if lang in long_langs:
      tuples.append((long_langs[lang],lang))
  return tuples    
  

def get_language_list(languages, current=''):
  """ given a list of ordered tuples with (Description, language_code), returns
    an Bootstrap-formatted unordered inline list. The current language will not be a link."""
  list_start = """<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle text-light" href="#" id="languageSelector" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
      <i class="fa-solid fa-language"></i>
    </a>
    <div class="dropdown-menu" aria-labelledby="languageSelector">
  """
  list_end = """
    </div>
  </li>
  """
  for language in languages:
    if language[1] == current:
      list_start += get_language_list_item(language, link=False)
    else:
      list_start += get_language_list_item(language)
  return list_start + list_end      

def get_language_list_item(language, link=True):
  """ Given an ordered tuple, returns a link to the current interview with lang=language code and the link title
    given in the first part of the tuple."""
  
  if link:
    return f"""<a class="dropdown-item" href="{ url_action('change_language', lang = language[1]) }">{ language[0] }</a>"""
  else:
    return f'<span class="dropdown-item-text">{ language[0] }</span>'
  

def get_language_list_inline(languages, current=''):
  """ given a list of ordered tuples with (Description, language_code), returns
    an Bootstrap-formatted unordered inline list. The current language will not be a link."""
  list_start = '<ul class="list-inline">'
  list_start += '<li class="list-inline-item"><b>Language</b>:</li>'
  list_end = '</ul>'
  for language in languages:
    if language[1] == current:
      list_start += get_language_list_item_inline(language, link=False)
    else:
      list_start += get_language_list_item_inline(language)
  return list_start + list_end      

def get_language_list_item_inline(language, link=True):
  """ Given an ordered tuple, returns a link to the current interview with lang=language code and the link title
    given in the first part of the tuple."""
  li_start = '<li class="list-inline-item">'
  li_end = '</li>'
  
  if link:
    iurl = url_action('change_language', lang = language[1])
    return li_start + '<a target="_self" href="' + iurl + '">' + language[0] + '</a>' + li_end
  else:
    return li_start + language[0] + li_end     