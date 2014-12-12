lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'cd images && find . && exit' >| '/media/sf_dropbox/Mosaic PNGs/image_list.txt'
lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'mirror --verbose=3 --reverse /home/kester/Dropbox/Mosaic\ PNGs/ /images && exit'
