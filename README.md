# pydlna
DLNA IN PYTHON 3

## how to use, you need proxy server for share stream

```python
from dlna import dlna
DLNARendererControllerInstance = dlna.DLNAController()
DLNARendererControllerInstance.discover(timeout=5)
devices = [(r, renderer.FriendlyName) for r, renderer in enumerate(DLNARendererControllerInstance.Renderers) if renderer.StatusAlive and bool(renderer.BaseURL)]
if devices:
    #select first device
    name = devices[0][1]
    r = devices[0][0]
    # send infomation to tv
    renderer = DLNARendererControllerInstance.Renderers[r]
    kind = 'video'
    size = ''
    duration = ''
    title = 'TEST'
    uri = '' # your local stream url
    DLNARendererControllerInstance.send_URI(renderer, uri, title, kind, size, duration)
    DLNARendererControllerInstance.send_Play(renderer)
    # to stop
    DLNARendererControllerInstance.send_Stop(renderer)
```
