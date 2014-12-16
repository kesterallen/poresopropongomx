set -e
set -x
lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'mirror --verbose=3 --reverse --delete /home/kester/Dropbox/Mosaic\ PNGs/ /images && exit'
lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'cd images && find . && exit' | perl -anle 'print substr($_, 2)' >| '/home/kester/Dropbox/Mosaic PNGs/image_list.txt'
ls /home/kester/Dropbox/Mosaic\ PNGs/*.{jpg,jpeg,png} | wc -l >| '/home/kester/Dropbox/Mosaic PNGs/image_count.txt'
cd /home/kester/Dropbox/Mosaic\ PNGs && lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'cd images && mput image*.txt && exit'
