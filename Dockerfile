FROM kivy/python-for-android:latest

WORKDIR /app
COPY . .

CMD ["python", "-m", "pythonforandroid.toolchain", "apk", \
    "--bootstrap=sdl2", "--dist_name=skyhop", \
    "--name=Sky Hop", "--version=1.0.0", "--package=com.skyhop.skyhop", \
    "--minsdk=21", "--ndk-api=21", \
    "--requirements=python3,kivy", \
    "--arch=arm64-v8a", \
    "--permission=INTERNET", \
    "--orientation=portrait", \
    "--copy-libs", "--debug"]
