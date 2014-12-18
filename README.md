

Upload new images with:

    lftp ftp.fatcow.com -e 'mirror --verbose=3 --reverse /home/kester/Dropbox/Mosaic\ PNGs/ /images && exit'

Deploy:

    lftp ftp.fatcow.com -e 'cd cgi-bin && mput *.py && exit'

