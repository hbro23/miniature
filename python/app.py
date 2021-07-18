from pathlib import Path
from re import match
from asyncio import create_task, run, sleep
from configparser import ConfigParser

from serial.tools.list_ports import comports as ports
from serial import Serial
from vlc import MediaPlayer
from keyboard import add_hotkey

LOOP_CHAPTER = 'LOOP'


class Video:

    class Chapter:

        def __init__(self, name, start, end, length):
            self.name = name
            self.start = start
            self.end = end
            self.start_position = float(start) / float(length)
            # print(self.start_position)

        def __repr__(self) -> str:
            return f'{self.start}-{self.end}ms | {self.start_position:.8f}%'

    def __init__(self, file, loop_start, loop_end, chapters):
        self.file = file
        self.__loop_start = loop_start
        self.__loop_end = loop_end
        self.chapters = chapters
        self.__current_chapter = ''
        self.on_chapter_change = None

        self.__load_player()

    def __load_player(self):
        folder, _ = get_video_path()
        path = folder / self.file
        self.__player = MediaPlayer(path)
        print(f'Loading video from {path}')
        self.__player.set_fullscreen(True)
        self.__player.video_set_key_input(True)

    @property
    def current_chapter(self):
        return self.__current_chapter

    @current_chapter.setter
    def current_chapter(self, new_chapter):
        chapter_data = self.chapters.get(new_chapter)

        print(f'SET CHAPTER {chapter_data}   | {bool(self.__player.is_seekable())}')
        time = self.__player.get_time()
        percentage = self.__player.get_position()
        print(f'CURRENT {time} -  {percentage} | SETTING ->  STAR: {chapter_data.start} | END: {chapter_data.end} ')

        if time < chapter_data.start  or time > chapter_data.end:  
            print(f'POSITION SETTED: {chapter_data.start_position}')
            self.__player.set_position(chapter_data.start_position)

        if self.on_chapter_change:
            create_task(self.on_chapter_change(
                new_chapter, self.__current_chapter))

        self.__current_chapter = new_chapter
        print()

    def set_listener(self, on_chapter_change):
        self.on_chapter_change = on_chapter_change

    async def play(self):

        def calculate_chapters():
            length = self.__player.get_length()
            previous = None
            new_chapters = {}
            for key in self.chapters:
                if previous is not None:
                    start = self.chapters[previous]
                    end = self.chapters[key] - 20
                    new_chapters[previous] = self.Chapter(
                        key, start, end, length)

                previous = key

            new_chapters[previous] = self.Chapter(previous,
                                                  self.chapters[previous], length, length)
            self.__final_chapter = new_chapters[previous]
            self.loop = self.Chapter(LOOP_CHAPTER,
                                     self.__loop_start, self.__loop_end, length)
            new_chapters[LOOP_CHAPTER] = self.loop
            self.chapters = new_chapters

        self.__player.play()
        await sleep(0.3)
        calculate_chapters()

        self.current_chapter = LOOP_CHAPTER

    def stop(self):
        self.__player.stop()

    def check_current_chapter(self):

        current_time = self.__player.get_time()
        print(f"TIME: {current_time} - {round(self.__player.get_position(), 4)}")

        if (self.current_chapter == LOOP_CHAPTER and current_time >= self.loop.end) \
                or (self.current_chapter == self.__final_chapter.name and round(self.__player.get_position(), 2) == 1):
            self.current_chapter = LOOP_CHAPTER
            return

        for name, chapter in self.chapters.items():
            if current_time >= chapter.start and current_time < chapter.end \
                    and self.current_chapter != name and name != LOOP_CHAPTER:
                print(f'CURRENT: {current_time} | FOUND: {chapter}')
                print("")
                
                self.current_chapter = name
                break



def get_video_path():

    folder = Path('videos')
    config_path = folder / 'chapters.config'

    return folder, config_path


def init_folder():

    def create_default_config():
        config = ConfigParser()
        general_section = {'video': 'nombre_del_video.mp4'}
        chapters_section = {'button_1': '6s',
                            'button_2': '10s', 'button_3': '20s'}
        loop_section = {'start': '0s', 'end': '5s'}

        config['GENERAL'] = general_section
        config['CHAPTERS'] = chapters_section
        config[LOOP_CHAPTER] = loop_section

        return config

    folder, config_path = get_video_path()

    exists = folder.exists() and config_path.exists()
    if not exists:
        folder.mkdir(parents=True, exist_ok=True)
        with config_path.open(mode='w', encoding='utf-8') as config_file:
            config = create_default_config()
            config.write(config_file)

    return exists


async def init_arduino(id):

    def search_port():
        for port in ports():
            if id in port.description:
                return port.device

    port = search_port()
    print(f'Setting up arduino on port: {port}')

    return Serial(port=port, baudrate=9600, timeout=0.05)


async def load_video():

    def parse_time(time):
        matches = match('(?:(\d*)m)?(?:(\d*)s)?', time)
        ms_time = 0
        if matches:
            minutes = int(matches.group(1) or 0)
            seconds = int(matches.group(2) or 0)

            ms_time = (minutes * 60 + seconds) * 1000

        return ms_time

    def parse_chapters(chapters):

        chapters = {chapter: time for chapter, time in chapters.items()}
        for chapter, time in chapters.items():
            chapters[chapter] = parse_time(time)

        print(f'Chapters: {chapters}')
        return chapters

    config = ConfigParser()
    _, config_path = get_video_path()
    config.read(config_path)

    video_file = config['GENERAL']['video']
    loop_start = parse_time(config[LOOP_CHAPTER]['start'])
    loop_end = parse_time(config[LOOP_CHAPTER]['end'])
    chapters = parse_chapters(config['CHAPTERS'])

    return Video(video_file, loop_start, loop_end, chapters)


async def main(id):

    def create_video_listener(arduino):
        async def on_chapter_change(new_chapter, old_chapter):
            data = f'{new_chapter}.'
            arduino.write(data.encode())
            print(f'SENDING: {data}')
            print()

        return on_chapter_change

    def on_escape_press(flag, arduino, player):
        flag['is_running'] = False
        arduino.write(b'STOP')
        player.stop()

    print(f'Staring main')

    exits_folder = init_folder()
    if not exits_folder:
        print("It's necessary config the application.")
        return

    task_arduino = create_task(init_arduino(id))
    task_video = create_task(load_video())
    await task_arduino
    await task_video

    with task_arduino.result() as arduino:
        video = task_video.result()
        await video.play()
        video.set_listener(create_video_listener(arduino))

        flag = {'is_running': True}
        add_hotkey('escape', on_escape_press,  args=(flag, arduino, video))

        while(flag['is_running']):
            chapter = arduino.readline()
            chapter = chapter.decode().rstrip()
            if chapter != '':
                if chapter.startswith('[LOG]'):
                    chapter = chapter.replace('[LOG]', '[ARDUINO LOG]')
                    print(chapter)
                
                if chapter.startswith('[CMD]'):
                    chapter = chapter.replace('[CMD]', '').lstrip()
                    print()
                    print(f'DATA RECEIVED: {chapter}')
                    print()
                    video.current_chapter = chapter

            video.check_current_chapter()
            await sleep(0.1)

    print(f'Ending main')


if __name__ == '__main__':
    ID_DEVICE = 'CH340'
    run(main(ID_DEVICE))
