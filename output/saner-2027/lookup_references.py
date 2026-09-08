import urllib.request,urllib.parse,json,concurrent.futures,pathlib
queries={'sagas':'Sagas Garcia Molina Salem','gray':'The transaction concept Virtues and limitations Gray','helland07':'Life beyond distributed transactions an apostates opinion','helland12':'Idempotence is not a medical condition','kahn':'Topological sorting of large networks','birdgit':'The promises and perils of mining Git','mrdt':'Mergeable replicated data types','swierstraloh':'The semantics of version control','hpt':'Homotopical patch theory','mimram':'A categorical theory of patches','edos':'Managing the complexity of large free and open source package based software distributions','adams':'Modern release engineering in a nutshell Why researchers should care','potvin':'Why Google stores billions of lines of code in a single repository','raemaekers':'Semantic versioning versus breaking changes A study of the Maven repository','bogart':'How to break an API Cost negotiation and community values in three software ecosystems','decan':'An empirical comparison of dependency network evolution in seven software packaging ecosystems','mokhov':'Build systems a la carte','klees':'Evaluating fuzz testing','pluto':'A sound and optimal incremental build system with dynamic dependencies','safety':'Defining liveness Alpern Schneider','lamporttime':'Time clocks and the ordering of events in a distributed system'}
def get(pair):
 key,q=pair
 try:
  url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':q,'rows':2})
  data=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ResearchBibliography/1.0'}),timeout=35))
  return key,data['message']['items']
 except Exception as e:return key,{'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: out=dict(ex.map(get,queries.items()))
pathlib.Path('output/saner-2027/research/crossref-candidates.json').write_text(json.dumps(out,indent=2))
for k,v in out.items():
 if isinstance(v,list):
  print(k,[(x.get('title'),x.get('DOI'),x.get('published',{}).get('date-parts')) for x in v])
 else:print(k,v)
