import ast, pathlib, json
def reverse(code_dir:pathlib.Path)->dict:
    models={}
    for py in code_dir.rglob("*.py"):
        tree=ast.parse(py.read_text(encoding='utf-8'))
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            fields={}
            for ann in [n for n in cls.body if isinstance(n, ast.AnnAssign)]:
                name=ann.target.id if isinstance(ann.target, ast.Name) else "field"
                ftype='str'
                if isinstance(ann.annotation, ast.Name):
                    ftype=ann.annotation.id
                fields[name]=ftype
            if fields:
                models[cls.name]=fields
    return {"title":"Reversed","models":models}
