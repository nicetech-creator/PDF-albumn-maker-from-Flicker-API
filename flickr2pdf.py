import sys
import os
import flickr_api
from bs4 import BeautifulSoup
from urllib.request import urlopen
from jinja2 import Environment, FileSystemLoader
import weasyprint


class Flickr2PDF:
    title = ""
    user = None
    username = ""
    path = ""
    id = 0
    page = None

    def __init__(self, url, key='e780392c82204d601eaaf715db9d2e4e', secret='c8aeddf10d814962'):
        flickr_api.set_keys(api_key=key, api_secret=secret)
        self.page = urlopen(url).read()
        self.user = flickr_api.Person.findByUrl(url)

    def get_title(self):
        soup = BeautifulSoup(self.page, "lxml")
        self.title = soup.find_all('meta',attrs={'name':'title'})[0]["content"]
        print("Album Title: " + self.title)
        return self.title

    def get_username(self):
        user_info = self.user.getInfo()
        self.username = user_info['username']
        print("Username: " + self.username)
        return self.username

    def get_photoid(self):
        ps = self.user.getPhotosets()
        for i,p in enumerate(ps):
            #print (i,p.title)
            if self.title == p.title:
                self.id = int(i)
                return i

    def makedir(self):
        self.path = "./"+self.username+"_"+str(self.id)
        print("Path: " + self.path)
        try:
            os.makedirs(self.path)
        except OSError:
            print ("Creation of the directory %s failed" % self.path)
        else:
            print ("Successfully created the directory %s " % self.path)

    def download_photos(self):
        photoset = self.user.getPhotosets()[self.id]
        for p in photoset.getPhotos() :
            print("Saving photo " + p.title)
            photo = p.title
            p.save(self.path+"/"+photo)

    def generate_pdf(self):
        imgs = sorted(
            [self.path+'/'+ i for i in os.listdir(self.path) if i.endswith(".jpg")]
        )
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('./template.html')
        output_from_parsed_template = template.render(imgs=imgs)
        with open("af.html", "w") as fh:
            fh.write(output_from_parsed_template)

        pdf = weasyprint.HTML('af.html').write_pdf()

        with open(self.username+" - "+self.title+".pdf", "wb") as f:
            f.write(pdf)

    def create_pdf(self):
        self.get_title()
        self.get_username()
        self.get_photoid()
        self.makedir()
        self.download_photos()
        self.generate_pdf()

if __name__ == '__main__':
    print("Creating PDF from: "+sys.argv[1])
    album = Flickr2PDF(sys.argv[1])
    album.create_pdf()
