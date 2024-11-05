import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from moviepy.editor import VideoFileClip
from vosk import Model, KaldiRecognizer
import wave
import json
import tempfile


# Путь к модели Vosk
vosk_model_path = "vosk-models\vosk-model-small-ru-0.22"
model = Model(vosk_model_path)


# Инициализация бота с токеном
TOKEN = '7576451428:AAF-OyMfm2u5okwwcW4wWSJTSkYts3WQDGY'
updater = Updater(TOKEN, use_context=True)


# Команда /start, чтобы приветствовать пользователя
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет! Отправь мне видео, и я преобразую его речь в текст.")


# Создание функции для обработки видео, извлечения аудио и распознавания речи
def handle_video(update: Update, context: CallbackContext) -> None:
    # Скачивание видеофайла от пользователя
    video_file = update.message.video.get_file()
    video_path = video_file.download()


    # Извлечение аудио из видео
    audio_path = tempfile.mktemp(suffix='.wav')
    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(audio_path)


    # Конвертация аудио в текст с помощью Vosk
    text = transcribe_audio_vosk(audio_path)
    if text:
        update.message.reply_text(f"Распознанный текст: {text}")
    else:
        update.message.reply_text("Не удалось распознать речь.")


    # Удаление временных файлов
    os.remove(video_path)
    os.remove(audio_path)


# Создание функции transcribe_audio_vosk, которая будет принимать путь к аудиофайлу и возвращать текст
def transcribe_audio_vosk(audio_path):
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:

        # Конвертируем аудио в нужный формат
        update.message.reply_text("Конвертируем аудио в подходящий формат для распознавания...")
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(audio_path, format="wav")

    recognizer = KaldiRecognizer(model, wf.getframerate())
    text = ""
    

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text += json.loads(result).get("text", "") + " "
    

    final_result = recognizer.FinalResult()
    text += json.loads(final_result).get("text", "")
    return text.strip()


# обработчики команд и видео для бота, а затем запуск его
def main():
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()




