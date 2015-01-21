

To deploy new images:
    A) Rename Dropbox images:
        Do imagemake.bash
        lftp ftp.fatcow.com -e 'mirror --verbose=3 --reverse images_numbered/ /images_numbered && exit'
    B) Generate a new image_count.txt file
        cd images_numbered
        find -type f  | wc -l > image_count.txt

#Upload new images with:
#
#    lftp ftp.fatcow.com -e 'mirror --verbose=3 --reverse /home/kester/Dropbox/Mosaic\ PNGs/ /images && exit'

Deploy:

    lftp ftp.fatcow.com -e 'cd cgi-bin && mput *.py && exit'
    lftp ftp.fatcow.com -e 'mirror --verbose=3 --reverse /home/kester/Dropbox/google_appengine/poresopropongomx/cgi-bin/ /cgi-bin && exit'
