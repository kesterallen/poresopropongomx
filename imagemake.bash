
# Make image_list.txt in the Mosaic PNG (also image_count.txt):
#
cd /home/kester/Dropbox/Mosaic\ PNGs
find 201* -type f | sort >| image_list.txt
wc -l image_list.txt | awk '{print $1}' >| image_count.txt

# TODO #cd /home/kester/Desktop/images_numbered
# TODO #find -type f  | wc -l > images_count.txt


Verify http://www.poresopropongo.mx/card/7735 and http://www.poresopropongo.mx/card/7421 are OK

# Mirror image directory, including the image_list.txt and image_count.txt files:
#
lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'mirror --verbose=3 --reverse --delete /home/kester/Dropbox/Mosaic\ PNGs/ /images && exit'
#TODO: lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'mirror --verbose=3 --reverse --delete /home/kester/Desktop/images_numbered  /images_numbered && exit'

