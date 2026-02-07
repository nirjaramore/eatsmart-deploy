import sys
from moviepy import VideoFileClip
from moviepy.video.fx.Crop import Crop


def crop_sides(infile, outfile, percent_each=10):
    clip = VideoFileClip(infile)
    w, h = clip.size
    p = float(percent_each) / 100.0
    x1 = int(w * p)
    x2 = int(w * (1 - p))
    # Apply Crop effect (x1,x2 are pixel coordinates)
    cropped = clip.with_effects([Crop(x1=x1, x2=x2)])
    cropped.write_videofile(outfile, codec="libx264", audio_codec="aac", preset="medium")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: crop_video.py <input> <output> [percent_each_side]")
        sys.exit(1)
    infile = sys.argv[1]
    outfile = sys.argv[2]
    pct = float(sys.argv[3]) if len(sys.argv) > 3 else 10
    crop_sides(infile, outfile, pct)
