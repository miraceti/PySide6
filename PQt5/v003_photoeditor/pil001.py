from PIL import Image, ImageFilter, ImageEnhance


with Image.open("PQt5/v003_photoeditor/images/imagesatellite1.png") as picture:
    #picture.show()

    black_white = picture.convert("L")
    black_white.save("PQt5/v003_photoeditor/images/gray.png")

    mirror = picture.transpose(Image.FLIP_LEFT_RIGHT)
    mirror.save("PQt5/v003_photoeditor/images/mirror.png")

    blur = picture.filter(ImageFilter.BLUR) 
    blur.save("PQt5/v003_photoeditor/images/blur.png") 

    contrast = ImageEnhance.Contrast(picture)
    contrast = contrast.enhance(2.5)
    contrast.save("PQt5/v003_photoeditor/images/contrast.png")

    color = ImageEnhance.Color(picture).enhance(2.5)
    color.save("PQt5/v003_photoeditor/images/color.png")

