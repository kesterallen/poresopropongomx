
# Make image_list.txt in the Mosaic PNG (also image_count.txt):
#
cd /home/kester/Dropbox/Mosaic\ PNGs
find 2* -type f | sort >| image_list.txt
wc -l image_list.txt | awk '{print $1}' >| image_count.txt
assert $(cat image_count.txt) == (wc -l image_list.txt)
cp image_* /home/kester/Desktop/images_numbered/
perl -lane '$src = $_; $dst = sprintf "/home/kester/Desktop/images_numbered/%07d/%010d.jpg", $./1000, $.; print  "cp $src $dst" if !-f $dst ' image_list.txt 
perl -lane '$src = $_; $dst = sprintf "/home/kester/Desktop/images_numbered/%07d/%010d.jpg", $./1000, $.; system "cp $src $dst" if !-f $dst ' image_list.txt 

# Mirror image directory, including the image_list.txt and image_count.txt files:
#
lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'mirror --verbose=3 --reverse --delete /home/kester/Desktop/images_numbered  /images_numbered && exit'

#Verify http://www.poresopropongo.mx/card/7735 and http://www.poresopropongo.mx/card/7421 are OK

