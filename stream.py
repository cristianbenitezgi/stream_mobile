from fastapi import FastAPI, HTTPException
import cv2
import subprocess
import threading

app = FastAPI()

procesodestreaming = None

def iniciarstream(host: str, stream_key: str):

    global procesodestreaming

    capture = cv2.capturadevideo(0)
    if not capture.isOpened():
        raise Exception("La camara no se pudo abrir")
    
    ffmpeg_comando = [
        'ffmpeg',
        '-f', 'rawvideo',
        '-pix-fmt', 'bgr24',
        '-s', f"{int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
        '-r', str(int(capture.get(cv2.CAP_PROP_FPS))),
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p'
        '-f', 'flv',
        f"rtmp://{host}/live/{stream_key}"
    ]

    procesodestreaming = subprocess.Popen(ffmpeg_comando, stdin=subprocess.PIPE)

    while True:
        ret, frame = capture.read()
        if not ret:
            break

        procesodestreaming.stdin.write(frame.tobytes())
    
    capture.release()
    procesodestreaming.stdin.close()
    procesodestreaming.wait()

@app.post("/iniciar_stream")
async def iniciar_stream(host: str, stream_key: str):
    global procesodestreaming

    if procesodestreaming and procesodestreaming.poll() is None:
        raise HTTPException(status_code=400, detail="Transmision en proceso, no se puede iniciar una nueva.")

