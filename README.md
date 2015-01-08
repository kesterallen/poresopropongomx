

To deploy new images:
    A) Rename Dropbox images:
        cat ../../Mosaic\ PNGs/image_list.txt | perl -lane 'printf qq!cp $_  images_numbered/%07d/%010d.jpg\n!, $./1000, $.'
        lftp ftp.fatcow.com -e 'mirror --verbose=3 --reverse images_numbered/ /images_numbered && exit'
    B) Generate a new image_count.txt file
        cd images_numbered
        find -type f  | wc -l > image_count.txt

Upload new images with:

    lftp ftp.fatcow.com -e 'mirror --verbose=3 --reverse /home/kester/Dropbox/Mosaic\ PNGs/ /images && exit'

Deploy:

    lftp ftp.fatcow.com -e 'cd cgi-bin && mput *.py && exit'

