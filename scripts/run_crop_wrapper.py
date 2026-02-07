from crop_video import crop_sides

infile = r"C:\Users\anany\projects\eatsmart\eatsmartwebsite\asset\From KlickPin CF Super Nonna → Illustration animation [Video] _ Graphic design posters Graphic design inspiration Branding design.mp4"
outfile = r"C:\Users\anany\projects\eatsmart\eatsmartwebsite\asset\Video Project 2.cropped.mp4"

if __name__ == '__main__':
    print('Cropping:', infile)
    crop_sides(infile, outfile, percent_each=10)
    print('Done')
