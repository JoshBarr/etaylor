# -----------------------------------------------------------------------------
# Album artwork generator
# -----------------------------------------------------------------------------
import textwrap
import eyed3
import shutil
import zipfile 
import errno
import os

# from Database import connect_db, get_db, close_db
from utils import mkdir_p
from wand.image import Image
from wand.display import display
from wand.drawing import Drawing, FONT_METRICS_ATTRIBUTES
from wand.color import Color
from random import randint, shuffle

from Album import Album
from up.Models import db, Answers, Artwork


import yaml
import json
import Image as PILImage

from hashids import Hashids


current_dir = os.path.dirname(os.path.realpath(__file__))
path_textwrap_data = os.path.join(current_dir, 'data/text-wraps.json')



class AlbumArtwork(object):
    artwork_template = "/static/album/up.png"
    foreground_template = os.path.join(current_dir,"static/images/placeholder-white.png")
    image_output_path = os.path.join(current_dir,"static/artwork/")
    track_input_path = os.path.join(current_dir,"var/tracks/")
    track_temp_path = os.path.join(current_dir,"var/download/")
    track_output_path = os.path.join(current_dir,"static/tracks/")
    artwork = None
    image_path = None
    thumbnail_path = None
    zip_file_path = None
    font = 'static/fonts/georgia.ttf'
    
    def create(self, hash_id, answer, random_answers):

        answer_id = answer.id
        image_path = '%sartwork-%s-500x500.png' % (self.image_output_path, hash_id)
        image_path_jpg = '%sartwork-%s-500x500.jpg' % (self.image_output_path, hash_id)
        thumbnail_path = '%sartwork-%s-140x140.png' % (self.image_output_path, hash_id)
        
        output_dir = os.path.join(current_dir, "static/tracks/%s" % (hash_id))
        zip_file_path = "%s/e-taylor-up-side-a.zip" % (output_dir)
        
        artwork = Artwork(
                answer_id  = answer_id,
                fullsize_url = image_path,
                fullsize_jpg = image_path_jpg,
                thumbnail_url = thumbnail_path, 
                zip_file = zip_file_path
            )

        db.session.add(artwork)
        db.session.commit()

        self.answer_id = answer_id
        self.image_path = image_path
        self.image_path_jpg = image_path_jpg
        self.thumbnail_path = thumbnail_path
        self.output_dir = output_dir
        self.zip_file_path = zip_file_path

        self.model = artwork 
        self.answer = answer

        self.random_answers = random_answers

        return self


    def render(self):

        all_answers = []
        
        random_answers = self.random_answers
        answer = self.answer.text


        for row in random_answers:
            all_answers.append(row.text)

        shuffle(all_answers)
        total_answers = len(all_answers)
        total_center = int(total_answers/2)

        # anywhere in the middle of the pack.
        user_answer_pos = randint(total_center - int(total_answers/4), total_center + int(total_answers/8))

        if user_answer_pos < 0:
            user_answer_pos = 0

        if user_answer_pos >= total_answers:
            user_answer_pos = total_answers


        all_answers.insert(user_answer_pos, answer)


        image_path = self.image_path
        thumbnail_path = self.thumbnail_path
        
        # num_lines = 28
        font_size = 20
        line_height = 1.8
        img_width = 1000
        gutters = 40

        px_line_height = int(font_size * line_height)
        num_lines = int((img_width - (30)) / px_line_height)        

        right_edge = img_width - gutters

        color_background = Color('#222')
        color_text = Color('#666')
        color_useranswer = Color('#D7605C')


        with open(path_textwrap_data) as data_file:
            text_wraps = json.load(data_file)

        with Image(filename=self.foreground_template) as original:
            with original.convert('png') as album_details:
                with Drawing() as draw:
                    with Color('white') as bg:
                        with Image(width=img_width, height=img_width, background=color_background) as image:
                            with Image(filename= os.path.join(current_dir, "static/images/placeholder-noise.png")) as noise:

                                # lowres_foreground.resize()


                                draw.fill_color = color_text

                                draw.font = os.path.join(current_dir,self.font)
                                draw.font_size = font_size

                                # _text = " / ".join(all_answers)

                                # lines = textwrap.wrap(_text, 45)

                                line_counter = 1
                                current_x = 0

                                for idx, answer in enumerate(all_answers):
                                    _text = "%s / " % (answer)

                                    if idx == user_answer_pos:
                                        draw.fill_color = color_useranswer
                                    else:
                                        draw.fill_color = color_text

                                    for char in _text.split(" "):

                                        if char and char != "":

                                            word = "%s " % (char)

                                            wrap_line = text_wraps[line_counter-1]

                                            metrics = draw.get_font_metrics(image, word, multiline=False) 
                                            # char_width = int(metrics.y1 + metrics.y2)
                                            char_width = int(metrics.text_width)
                                            # print metrics
                                            for wrap in wrap_line:
                                                # print wrap
                                                if current_x + char_width > wrap[0] - 5:
                                                    if current_x + char_width < wrap[1] + 15:
                                                        current_x = wrap[1] + 15
                                                        # print current_x

                                            if  current_x < right_edge - char_width - gutters:


                                                draw.text(gutters + (current_x), 15 + (px_line_height * line_counter), word)
                                                current_x += char_width

                                            else:
                                                if line_counter < num_lines:
                                                    line_counter += 1
                                                    current_x = 0
                                                    draw.text(gutters + (current_x), 15 + (px_line_height * line_counter), word)
                                                    current_x += char_width


                                        # print draw.get_font_metrics(image, char, multiline=False)    
                                        # draw.text(gutters, gutters + (px_line_height * line_counter), char)
                                        # line_counter = line_counter+1
                                
                                draw(image)
                                
                                # image.composite(noise, left=0, top=0)
                                image.composite(album_details, left=-10, top=int(gutters/1.5))
                                
                                image.save(filename=image_path)

                                im = PILImage.open(image_path)
                                jpeg = image_path.replace(".png", ".jpg")
                                if im.mode != "RGB":
                                    im = im.convert("RGB")
                                im.save(jpeg)


        with Image(filename=image_path) as large:
            with large.clone() as thumb:
                thumb.resize(140, 140)
                thumb.save(filename=thumbnail_path)
            

       
        return self.zip_file_path 


    def copy_track(self, song, answer_id):
        song_input_filename = "%s%s" % (self.track_input_path, song['filename'])
        song_output_filename = "%s%s/%s" % (self.track_temp_path, answer_id, song['filename'])
        
        print "copying: ", song_input_filename, song_output_filename
        shutil.copy2(song_input_filename, song_output_filename)

        return song_output_filename

    def process(self, answer_id, hash_id):
        album_data = self.get(answer_id)

        return self.process_tracks(
            answer_id,
            hash_id,
            os.path.join(current_dir, album_data.fullsize_url),
            os.path.join(current_dir, album_data.thumbnail_url),
            os.path.join(current_dir, album_data.zip_file)
        )


    def process_tracks(self, answer_id, hash_id, image_path, thumbnail_path, zip_output):
        output_dir = "%s%s" % (self.track_output_path, hash_id)
        temp_dir = "%s%s" % (self.track_temp_path, hash_id)
        image_data = open(image_path, "rb").read()
        thumbnail_data = open(thumbnail_path, "rb").read()

        # print image_path

        # Get an album instance (they're all the mother flippin same...)
        album = Album()

        print zip_output

        if not os.path.exists(zip_output):
            
            if not os.path.exists(temp_dir):
                mkdir_p(temp_dir)

            if not os.path.exists(output_dir):
                mkdir_p(output_dir)

            track_counter = 1;

            for song in album.tracks:
                song_output_filename = self.copy_track(song, hash_id)

                audiofile = eyed3.load(song_output_filename)
                # print audiofile.tag
                # print song_output_filename

                if not audiofile.tag:
                    audiofile.tag = eyed3.id3.Tag()
                    audiofile.tag.file_info = eyed3.id3.FileInfo(song_output_filename)

                audiofile.tag.artist = u"%s" % ( album.artist )
                audiofile.tag.album = u"%s" % ( album.title )
                audiofile.tag.title = u"%s" % ( song['title'] )
                audiofile.tag.track_num = track_counter

                audiofile.tag.images.set(2, image_data, "image/png", u"%s - %s" % (album.artist, album.title))
                
                audiofile.tag.save(preserve_file_time=True, version=eyed3.id3.ID3_V2_4)
                track_counter = track_counter + 1
            
            self.zip(temp_dir, zip_output, image_path)

        return zip_output

    def zip(self, src, dst, image_path):
        with zipfile.ZipFile("%s" % (dst), "w") as zf:
            abs_src = os.path.abspath(src)

            for dirname, subdirs, files in os.walk(src):
                for filename in files:
                    absname = os.path.abspath(os.path.join(dirname, filename))
                    arcname = absname[len(abs_src) + 1:]
                    print 'zipping %s as %s' % (os.path.join(dirname, filename),
                                                arcname)
                    zf.write(absname, arcname)

            zf.write(image_path, "artwork.png")
            zf.close()
            shutil.rmtree(src)


    def get(self, answer_id=1):
        artwork = Artwork.query.filter_by(answer_id=answer_id).first()
        return artwork
            

    def get_by_answer(self, answer_id=1):
        artwork = Artwork.query.filter_by(answer_id=answer_id).first()
        return artwork

    def __exit__(self, *err):
        pass

    def __enter__(self):
        return self

    # def __del__(self):
    #     print "deling", self



def strip_path(path):
    base_path = current_dir
    base = os.path.commonprefix([current_dir, path])
    path = path.replace(base, "")
    return path



