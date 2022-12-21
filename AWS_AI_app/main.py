import boto3
import json
from PIL import Image, ImageDraw, ImageFont

# Amazon Translate client
translate = boto3.client('translate')

# Amazon Textract client
textract = boto3.client('textract')

# Amazon Polly client
polly = boto3.client('polly')

# set the font
font_family = "arial.ttf"

# Document to translate
#documentName = "lorem_ipsum_en.png"
documentName = "test_en_full.png"

# Read document content
with open(documentName, 'rb') as document:
    imageBytes = bytearray(document.read())

# Call Amazon Textract
data = textract.detect_document_text(Document={'Bytes': imageBytes})

# full string that is in the image
str = ""

# get an image
with Image.open(documentName).convert("RGBA") as base:

    # extract the size from the image
    width = base.size[0]
    height = base.size[1]

    # make a blank image for the text, initialized to transparent text color
    txt = Image.new("RGBA", base.size, (255, 255, 255, 0))

    # load the font
    font = ImageFont.load_default()

    # get a drawing context
    d = ImageDraw.Draw(txt)

    for item in data["Blocks"]:
        if item["BlockType"] == "LINE":     # for every line of text on the image

            # coordinates of the polygon
            coords = []

            # extract the coordinates
            for c in item["Geometry"]["Polygon"]:
                coords.append((int(c["X"]*width), int(c["Y"]*height)))

            # give text with a higher confidence a lighter background
            conf = int(item["Confidence"])

            # draw the polygon
            d.polygon(coords, fill=(150+conf, 150+conf, 150+conf, 255), outline=None)

            # extract the boundry box position
            left = item["Geometry"]["BoundingBox"]["Left"]
            top = item["Geometry"]["BoundingBox"]["Top"]

            # translate the text to Dutch
            result = translate.translate_text(Text=item["Text"], SourceLanguageCode="auto", TargetLanguageCode="nl")
            text = result.get('TranslatedText')

            str += text + " "

            # extract the size of the box
            w = int(item["Geometry"]["BoundingBox"]["Width"]*width)
            h = int(item["Geometry"]["BoundingBox"]["Height"] * height)

            # scale the font size to the size of the bounding box
            # https://stackoverflow.com/a/4902713
            fontsize = 1  # starting font size
            font = ImageFont.truetype(font_family, fontsize)
            while font.getsize(text)[0] < w and font.getsize(text)[1] < h:
                # iterate until the text size is just larger than the criteria
                fontsize += 1
                font = ImageFont.truetype(font_family, fontsize)

            # optionally de-increment to be sure it is less than criteria
            fontsize -= 1
            font = ImageFont.truetype(font_family, fontsize)

            # draw the text on top of the polygon
            d.text((int(left * width), int(top * height)), text, fill=(0, 0, 0, 255), font=font)

    # add the text on top of the base image
    out = Image.alpha_composite(base, txt)

    #out.save("RESULT.png")

    # show the result
    out.show()

# text to speech in Dutch voice
response = polly.synthesize_speech(VoiceId='Laura', OutputFormat='mp3', Text = str, Engine = 'neural')

file = open('speech.mp3', 'wb')
file.write(response['AudioStream'].read())
file.close()
