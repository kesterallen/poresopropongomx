

To deploy new images:
    A) Rename Dropbox images, make a new image_list and image_count file, and copy them to a staging dir:
        cd /home/kester/Dropbox/Mosaic\ PNGs
        find 2* -type f | sort >| image_list.txt
        wc -l image_list.txt | awk '{print $1}' >| image_count.txt

        assert $(cat image_count.txt) == (wc -l image_list.txt)

        cp image_*.txt /home/kester/Desktop/images_numbered/
        perl -lane '$src = $_; $dst = sprintf "/home/kester/Desktop/images_numbered/%07d/%010d.jpg", $./1000, $.;  print "cp $src $dst" if !-f $dst ' image_list.txt 
        perl -lane '$src = $_; $dst = sprintf "/home/kester/Desktop/images_numbered/%07d/%010d.jpg", $./1000, $.; system "cp $src $dst" if !-f $dst ' image_list.txt 

    B) FTP to site:
        lftp ftp.fatcow.com -e 'mirror --verbose=3 --reverse images_numbered/ /images_numbered && exit'

    C) Verify trouble spots are OK:
        http://www.poresopropongo.mx/card/7735
        http://www.poresopropongo.mx/card/7421

Deploy html and py files:

    lftp ftp.fatcow.com -e 'mput *.html && mirror --verbose=3 --reverse /home/kester/Dropbox/google_appengine/poresopropongomx/cgi-bin/ /cgi-bin && exit'
