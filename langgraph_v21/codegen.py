import pathlib, jinja2, json
def generate(spec,out:pathlib.Path):
    env=jinja2.Environment(loader=jinja2.FileSystemLoader((pathlib.Path(__file__).parent/'templates')))
    app_dir=out/'app'; core=app_dir/'core'; api=app_dir/'api'
    for d in (core,api): d.mkdir(parents=True, exist_ok=True)
    ctx={'models':spec['models'],'title':spec['title']}
    core.joinpath('models.py').write_text(env.get_template('models.py.j2').render(**ctx))
    api.joinpath('router.py').write_text(env.get_template('router.py.j2').render(**ctx))
    app_dir.joinpath('main.py').write_text(env.get_template('main.py.j2').render(**ctx))
    for p in (core,api,app_dir): p.joinpath('__init__.py').write_text('',encoding='utf-8')
    app_dir.joinpath('SPEC.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
