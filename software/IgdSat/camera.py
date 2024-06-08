import io
import asyncio
from aiohttp import web
import logging
import socketserver
from asyncio import Condition
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from libcamera import Transform
import time
import simplejpeg
import random

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None

        self.VideoFile = open("/home/igdsat/IgdSat-MPU/VIDEO/%s.mjpeg" % random.randint(0,999999999),"wb")
        self.condition = Condition()

    async def Async_write(self, buf):  
        async with self.condition:
            self.frame = buf
            self.condition.notify_all()
            self.VideoFile.write(b"\n\n--my_mjpeg_boundary\nContent-Type: image/jpeg\n\n")
            self.VideoFile.write(buf)


    def write(self, buf):
        if buf == b"":
            return
        asyncio.run(self.Async_write(buf))


async def handle(request):
    if request.path == '/':
        return web.HTTPFound(location='/index.html')
    elif request.path == '/index.html':
        content = PAGE.encode('utf-8')
        return web.Response(body=content, content_type='text/html')
    elif request.path == '/stream.mjpg':
        print("returning")
        response = web.StreamResponse()
        
        response.content_type = 'multipart/x-mixed-replace; boundary=FRAME'
        await response.prepare(request)
        try:
            while True:
                #async with output.condition:
                #    await output.condition.wait()
                #    frame = output.frame
                await asyncio.sleep(0.2)
                frame = output.frame
                await response.write(b'--FRAME\r\n')
                await response.write(b'Content-Type: image/jpeg\r\n\r\n')
                await response.write(frame)
                await response.write(b'\r\n')
        except ConnectionResetError:
            return response


class SubEncoder(JpegEncoder):
    def encode_func(self, request, name):

        # Limit the framerate to reduce workload
        if not hasattr(self,"last"):
            self.last = time.time()
        Iterator = 0
        if self.igdsat.Active:
            Iterator = 1/30
        else:
            Iterator = 1/5
        if (time.time() - self.last) < Iterator: # 5fps or 30fps
            return b""
        self.last=time.time()

        if self.colour_space is None:
            self.colour_space = self.FORMAT_TABLE[request.config[name]["format"]]
        array = request.make_array(name)
        return simplejpeg.encode_jpeg(array, quality=self.q, colorspace=self.colour_space,
                                      colorsubsampling=self.colour_subsampling)


picam2 = Picamera2()
conf = picam2.create_video_configuration(main={"size": (1536, 864) } , transform=Transform(vflip=True) )
picam2.configure(conf)
#conf["controls"]["FrameDurationLimits"] = (40000,40000)
#picam2.configure(conf)
output = StreamingOutput()
encoder = SubEncoder(q=35)
picam2.start_recording(encoder, FileOutput(output))

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_get('/index.html', handle)
    app.router.add_get('/stream.mjpg', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8000)
    await site.start()


#loop = asyncio.get_event_loop()
#loop.run_until_complete(run_web_server())
