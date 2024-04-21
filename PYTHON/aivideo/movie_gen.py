import json, os
from moviepy.editor import TextClip, AudioFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips

WIDTH = 1920
HEIGHT = 1080
FONT_PATH = 'Inter/static/Inter-Regular.ttf'

# TODO
# make it crossfade between the slide
# see if there's a faster way to render the video

def make_aivideo(clips, width: int = WIDTH, height: int = HEIGHT, output: str = 'output.webm'):
    if os.path.exists(clips):
        with open(clips, 'r') as f:
            clips = json.load(f)

    def make_txt_clip(text: str, width: int, height: int, font_path: str):
        new_text = text.replace('- ', '⚫︎ ')
        font_size = 48
        clip = TextClip(new_text, fontsize=font_size, color='black', bg_color='white', font=font_path, method='caption', size=(width, None))
        while clip.size[1] > height and font_size > 10:  # Reduce font size if text doesn't fit
            print('resizing the clip, this might take a while...')
            font_size -= 2
            clip = TextClip(new_text, fontsize=font_size, color='black', bg_color='white', font=font_path, method='caption', size=(width, None))
        return clip.set_position('center')

    video_clips = []
    for clip in clips:
        audio_clip = AudioFileClip(clip['Clip #'])

        #this is where the text can be modified to be further summarized or whatever
        text = clip['Clip Text']

        txt_clip = make_txt_clip(text, WIDTH, HEIGHT, FONT_PATH)
        txt_clip = txt_clip.set_audio(audio_clip)
        txt_clip = txt_clip.set_duration(audio_clip.duration)
        
        white_bg = ColorClip((WIDTH, HEIGHT), color=(255, 255, 255), duration=audio_clip.duration)
        
        slide = CompositeVideoClip([white_bg, txt_clip])
        video_clips.append(slide)

    final_clip = concatenate_videoclips(video_clips, method='compose')
    final_clip.write_videofile(output, fps=24, threads=8, codec='libvpx') # go faster holy shit
    final_clip.close()

if __name__ == '__main__':
    make_aivideo('clips.json')
    # Usage
    #make_aivideo('clips.json', width=1280, height=720, output='huh.webm')
    # you can also pass in a dict directly into the first parameter