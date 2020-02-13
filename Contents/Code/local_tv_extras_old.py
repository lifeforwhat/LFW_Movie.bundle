#local media assets agent
import os, string, re
  
def FindShowDir(dirs):
  final_dirs = {}
  for dir in dirs:
    #final_dirs[dir] = True #uncomment this line if you also want to search for extras in the season folder
    try:
      parent = os.path.split(dir)[0]
      final_dirs[parent] = True
    except:pass
  
  if final_dirs.has_key(''):
    del final_dirs['']
  return final_dirs
  
def FindExtras(metadata, paths):
  # Do a quick check to make sure we've got the extra types available in this framework version,
  # and that the server is new enough to support them.
  #
  try: 
    t = InterviewObject()
    if Util.VersionAtLeast(Platform.ServerVersion, 0,9,9,13):
      find_extras = True
    else:
      find_extras = False
      Log('Not adding extras: Server v0.9.9.13+ required')
  except NameError, e:
    Log('Not adding extras: Framework v2.5.0+ required')
    find_extras = False
    
  if find_extras:
    extra_type_map = {'trailer' : TrailerObject,
                'deleted' : DeletedSceneObject,
                'behindthescenes' : BehindTheScenesObject,
                'interview' : InterviewObject,
                'scene' : SceneOrSampleObject,
                'featurette' : FeaturetteObject,
                'short' : ShortObject,
                'other' : OtherObject}
    VIDEO_EXTS          = ['3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bivx', 'bup', 'divx', 'dv', 'dvr-ms', 'evo', 'fli', 'flv', 'm2t', 'm2ts', 'm2v', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nsv', 'nuv', 'ogm', 'ogv', 'tp', 'pva', 'qt', 'rm', 'rmvb', 'sdp', 'svq3', 'strm', 'ts', 'ty', 'vdr', 'viv', 'vob', 'vp3', 'wmv', 'wpl', 'wtv', 'xsp', 'xvid', 'webm']
    for path in paths:
      #path = helpers.unicodize(path) 
      extras = []
      re_strip = Regex('[\W ]+')
      
      Log('Looking for local extras in path: '+ path)
      for root, dirs, files in os.walk(path):
        for d in dirs:
          for key in extra_type_map.keys():
            if re_strip.sub('', d.lower()).startswith(key):
              #Log("%s directory found", key)
              for f in os.listdir(os.path.join(root, d)):
                (fn, ext) = os.path.splitext(f)
                if not fn.startswith('.') and ext[1:].lower() in VIDEO_EXTS:
                  # On Windows, os.walk() likes to prepend the "extended-length path prefix" to root.
                  # This causes issues later on when this path is converted to the file:// URL for
                  # serialization and later consumption by PMS, so clean it up here.
                  #
                  root = re.sub(r'^\\\\\?\\', '', root)
                  
                  Log('Found %s extra: %s' % (key, f))
                  extras.append({'type' : key, 'title' : fn, 'file' : os.path.join(root, d, f)})
              continue
              
      # Look for filenames following the "-extra" convention and a couple of other special cases.
      for f in os.listdir(path):
        (fn, ext) = os.path.splitext(f)

        # Files named exactly 'trailer' or starting with 'movie-trailer'.
        if (fn == 'trailer' or fn.startswith('movie-trailer')) and not fn.startswith('.') and ext[1:] in config.VIDEO_EXTS:
          Log('Found trailer extra, renaming with title: ' + media_title)
          extras.append({'type' : key, 'title' : media_title, 'file' : os.path.join(path, f)})

        # Files following the "-extra" convention.
        else:
          for key in extra_type_map.keys():
            if not fn.startswith('.') and fn.endswith('-' + key) and ext[1:] in VIDEO_EXTS:
              Log('Found %s extra: %s' % (key, f))
              title = ' '.join(fn.split('-')[:-1])
              extras.append({'type' : key, 'title' : title, 'file' : os.path.join(path, f)})
  
      # Make sure extras are sorted alphabetically and by type.
      type_order = ['trailer', 'behindthescenes', 'interview', 'deleted', 'scene', 'sample', 'featurette', 'short', 'other']
      extras.sort(key=lambda e: e['title'])
      extras.sort(key=lambda e: type_order.index(e['type']))
      
      for extra in extras:
        metadata.extras.add(extra_type_map[extra['type']](title=extra['title'],file=extra['file']))
        #Log(extra['file'])
      
      Log('added %d extras' % len(metadata.extras))
      Log('finished')

"""
class localTVExtra(Agent.TV_Shows):
  name = 'Local TV Extras Agent'
  languages = [Locale.Language.NoLanguage]
  primary_provider = False
  persist_stored_files = False
  #contributes_to = ['com.plexapp.agents.thetvdb', 'com.plexapp.agents.themoviedb', 'com.plexapp.agents.hama', 'com.plexapp.agents.none']

  def search(self, results, media, lang):
    results.Append(MetadataSearchResult(id = 'null', score = 100))

  def update(self, metadata, media, lang):
    dirs = {}
    for s in media.seasons:
      #Log('Current Season %s', s)
      metadata.seasons[s].index = int(s)
      for e in media.seasons[s].episodes:
        episodeMetadata = metadata.seasons[s].episodes[e]
        episodeMedia = media.seasons[s].episodes[e].items[0]
        directory = os.path.dirname(episodeMedia.parts[0].file)
        dirs[directory] = True
    
    Log('directories are: %s', string.join(dirs, ", "))
    
    showfolder = False;
    for d in dirs:
      if os.path.basename(d).lower().startswith(('season','specials')):
        Log("%s is a Season Folder", os.path.basename(d))
      else:
        Log("Folder name, %s doesn't include \"Season\" or \"Specials\" so it must be a Show Folder", os.path.basename(d))
        showfolder = True;

    if(showfolder == False):
      try: dirs = FindShowDir(dirs)
      except: dirs = []
    
    Log('directory to search for extras: %s', string.join(dirs, ", "))
    
    FindExtras(metadata, dirs)
"""
def update(metadata, media):
  dirs = {}
  for s in media.seasons:
    #Log('Current Season %s', s)
    metadata.seasons[s].index = int(s)
    for e in media.seasons[s].episodes:
      episodeMetadata = metadata.seasons[s].episodes[e]
      episodeMedia = media.seasons[s].episodes[e].items[0]
      directory = os.path.dirname(episodeMedia.parts[0].file)
      dirs[directory] = True
  
  Log('directories are: %s', string.join(dirs, ", "))
  
  showfolder = False
  for d in dirs:
    if os.path.basename(d).lower().startswith(('season','specials')):
      Log("%s is a Season Folder", os.path.basename(d))
    else:
      Log("Folder name, %s doesn't include \"Season\" or \"Specials\" so it must be a Show Folder", os.path.basename(d))
      showfolder = True

  if(showfolder == False):
    try: dirs = FindShowDir(dirs)
    except: dirs = []
  
  Log('directory to search for extras: %s', string.join(dirs, ", "))
  
  FindExtras(metadata, dirs)             
