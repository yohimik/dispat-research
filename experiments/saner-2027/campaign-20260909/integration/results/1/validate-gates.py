import json
p=json.load(open('packages.json'))
assert p and all(v.get('scripts',{}).get('tests') for v in p.values()), 'required package test missing'
