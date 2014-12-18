set -e
set -x

# Make image_list.txt in the Mosaic PNG (also image_count.txt):
#
cd /home/kester/Dropbox/Mosaic\ PNGs
cp image_list_oldpngs.txt image_list.txt
find 201?????-?? -type f | sort >> image_list.txt
wc -l image_list.txt | awk '{print $1}' >| image_count.txt

# Mirror image directory, including the image_list.txt and image_count.txt files:
#
lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'mirror --verbose=3 --reverse --delete /home/kester/Dropbox/Mosaic\ PNGs/ /images && exit'

