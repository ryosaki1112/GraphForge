import difflib, json, pathlib
def diff(old_spec:dict,new_spec:dict,out:pathlib.Path):
    old=json.dumps(old_spec,ensure_ascii=False,indent=2).splitlines()
    new=json.dumps(new_spec,ensure_ascii=False,indent=2).splitlines()
    text="\n".join(difflib.unified_diff(old,new,fromfile='old',tofile='new',lineterm=''))
    out.write_text(text,encoding='utf-8')
