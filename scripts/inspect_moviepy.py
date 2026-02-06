import moviepy, os
p = os.path.dirname(moviepy.__file__)
print('moviepy package path:', p)
print('\n'.join(os.listdir(p)))
print('\nChecking for editor module:')
print(os.path.exists(os.path.join(p, 'editor.py')))
print(os.path.exists(os.path.join(p, 'editor')))
print('\nChecking for video subpackage:')
print(os.path.exists(os.path.join(p, 'video')))
print('\nAttempt to import VideoFileClip from known locations:')
try:
    from moviepy.editor import VideoFileClip
    print('imported from moviepy.editor')
except Exception as e:
    print('moviepy.editor import failed:', e)
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    print('imported from moviepy.video.io.VideoFileClip')
except Exception as e:
    print('moviepy.video.io.VideoFileClip import failed:', e)
try:
    from moviepy.video.VideoClip import VideoClip
    print('imported VideoClip from moviepy.video.VideoClip')
except Exception as e:
    print('moviepy.video.VideoClip import failed:', e)
