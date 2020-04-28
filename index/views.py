from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pytube import YouTube
import threading
from cv2 import cv2
import ffmpeg
import math

saveThread = []

streamVideo = []
streamAudio = []
streamsNorm = []

def checkThread():
    if(len(saveThread) > 0):
        saveThread[0].kill()
        saveThread[0].join()
        saveThread.clear()


#загрузка главной страницы
def index(request):
    streamVideo.clear()
    streamAudio.clear()
    checkThread()
    return render(request, 'index.html')


#1. получение всех видео потоков
#2. получение всех аудио потоков
#3. определение все возможных качество видео
def info(request):
    streamAudio.clear()
    streamVideo.clear()
    checkThread()
    yt = YouTube(request.POST['textRef'])
    sVideo = yt.streams.filter(type='video', mime_type='video/webm') #фильтрация видео потоков
    sAudio = yt.streams.filter(type='audio', mime_type='audio/webm') #фильтрация аудио потоков

    #метаданные о видео + ссылка
    for video in sVideo:
        if (video.fps != 60):
            streamVideo.append({
                'res': video.resolution,
                'mime_type': video.mime_type,
                'url': video.url,
                'subtype': video.subtype,
                'vcodec': video.video_codec,
                'filesize': video.filesize
            })

    #метаданные о аудио + ссылка
    for audio in sAudio:
        streamAudio.append({
            'mime_type': audio.mime_type,
            'url': audio.url,
            'subtype': audio.subtype,
            'acodec': audio.audio_codec,
            'abr': audio.abr,
            'filesize': audio.filesize,
        })

    #все качества video
    array = []
    for capacity in streamVideo:
        if (capacity['res'] != "None"):
            if (capacity['res'] not in array):
                array.append(int(str(capacity['res']).replace('p', '')))

    #сортировка по убыванию
    array.sort(reverse=True)

    #всё в один текст
    text = ""
    for c in array:
        text += str(c) + 'p/'

    return JsonResponse({
        'capacitys': text,
        'title': yt.title,
    })


#выбор url ссылок видео потока и аудио потока
#определение кодеков видео и аудио
#определение fps и продолжительность виео
def creat(request):
    checkThread()
    for video in streamVideo:
        if (video['res'] == request.POST['res']):
            mime_type = video['mime_type']
            video_codec = video['vcodec']
            urlV = video['url']
            fps = cv2.VideoCapture(urlV).get(cv2.CAP_PROP_FPS)
            duration = cv2.VideoCapture(urlV).get(cv2.CAP_PROP_FRAME_COUNT) / fps
            height = cv2.VideoCapture(urlV).get(cv2.CAP_PROP_FRAME_HEIGHT)
            width = cv2.VideoCapture(urlV).get(cv2.CAP_PROP_FRAME_WIDTH)

    for audio in streamAudio:
        if (int(str(request.POST['res']).replace('p', '')) >= 720):
            if (audio['abr'] == '160kbps' or audio['abr'] == '128kbps'):
                audio_codec = audio['acodec']
                urlA  = audio['url']
        elif (int(str(request.POST['res']).replace('p', '')) >= 360 and int(str(request.POST['res']).replace('p', '')) <= 480):
            if (audio['abr'] == '70kbps'):
                audio_codec = audio['acodec']
                urlA  = audio['url']
        elif (int(str(request.POST['res']).replace('p', '')) >= 144 and int(str(request.POST['res']).replace('p', '')) <= 240):
            if (audio['abr'] == '50kbps'):
                audio_codec = audio['acodec']
                urlA  = audio['url']

    saveThread.append(Load(urlV, urlA, fps, height, width))
    saveThread[0].start()

    return JsonResponse({
        'mime_type': mime_type,
        'vcodec': video_codec,
        'acodec': audio_codec,
        'duration': duration,
    })


def chunkGet(request):
    while True:
        if (len(saveThread[0].saveChunkVideo) > 0):
            break
    return HttpResponse(saveThread[0].get())


class Load(threading.Thread):
    def __init__(self, urlV, urlA, fps, height, width):
        threading.Thread.__init__(self)
        self.killThread = False
        self.isLoadingStop = False
        self.saveChunkVideo = []

        self.height = height
        self.width = width

        self.urlVideo = urlV
        self.streamAudio = (
            ffmpeg
            .input(urlA, f='webm')
        )

        self.process = (
            ffmpeg
            .input(self.urlVideo, format='webm')
            .output(self.streamAudio, 'pipe:', format='webm', r=fps, s='{}x{}'.format(int(self.width), int(self.height)), vcodec='copy', acodec='copy', **{'q:a': 1, 'q:v': 1})
            .run_async(pipe_stdout=True)
        )

    def run(self):
        while True:
            if (not self.killThread):
                if (not self.isLoadingStop):
                    chunk_in_bytes = self.process.stdout.read(int(self.height) * int(self.width) * 2)

                    if not chunk_in_bytes:
                        break

                    self.saveChunkVideo.append(chunk_in_bytes)
            elif (self.killThread):
                break

    def get(self):
        buf = self.saveChunkVideo.pop(0)
        return buf

    def kill(self):
        self.killThread = True