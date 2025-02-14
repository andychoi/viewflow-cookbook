# FSM 101

Finite state machine workflow UI and REST API

## Online demo

https://demo-next.viewflow.io/review/

## Quickstart

```bash
$ git clone https://github.com/viewflow/cookbook.git

$ python3 -m venv fsm101/venv
$ source fsm101/venv/activate

$ pip install fsm101/requirements.txt --extra-index-url=...
$ python3 fsm101/manage.py migrate
$ python3 fsm101/manage.py runserver
```

Navigate to http://127.0.0.1:8000

## Related documentation
- [FSM Workflow](https://docs-next.viewflow.io/fsm/index.html)

## Most interesting files
- [flows.py](./review/flows.py) - FSM workflow definition
- [admin.py](./review/admin.py) - Django admin integration
- [rest.py](./review/rest.py) - Generic REST API
- [viewset.py](./review/viewset.py) - Generic template based UI
