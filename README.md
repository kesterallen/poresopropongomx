

To deploy new images:
    A) Make new image list/count files and cop them to staging dir:
        cd /home/kester/Dropbox/Mosaic\ PNGs
        find 2* -type f | sort >| image_list.txt
        wc -l image_list.txt | awk '{print $1}' >| image_count.txt

        len1=$(cat image_count.txt)
        len2=$(wc -l image_list.txt | awk '{print $1}')
        if [ $len1 == $len2 ]; then echo "Good to go: $len1 images"; else echo "STOP STOP STOP $len1 != $len2"; fi

        cp image_*.txt /home/kester/Desktop/images_numbered/

    B) Rename Dropbox images, make a new image_list and image_count file, and copy them to a staging dir:
        perl -lane '$src = $_; $dst = sprintf "/home/kester/Desktop/images_numbered/%07d/%010d.jpg", $./1000, $.;  print "cp $src $dst" if !-f $dst ' image_list.txt
        perl -lane '$src = $_; $dst = sprintf "/home/kester/Desktop/images_numbered/%07d/%010d.jpg", $./1000, $.; system "cp $src $dst" if !-f $dst ' image_list.txt

    C) Deploy images, and image_list/image_count files;
       put new li elements for navbar in galleries.html;
       and deploy html and py files:

        cd /home/kester/Dropbox/google_appengine/poresopropongomx
        lftp ftp.fatcow.com -e 'mirror --exclude-glob image_*txt --verbose=3 --reverse /home/kester/Desktop/images_numbered/ /images_numbered && exit'

        perl -lane '$m = int($_/100); printf qq!              <li><a href="/%s">Galerías %s</a></li>\n!, ($m-$_)*100, $_ for 1..$m' /home/kester/Desktop/images_numbered/image_count.txt >| galleries.html
        cat navbar_head.html galleries.html navbar_tail.html >| navbar.html
        lftp ftp.fatcow.com -e 'mput *.html && exit'
        lftp ftp.fatcow.com -e 'mirror --verbose=3 --reverse /home/kester/Dropbox/google_appengine/poresopropongomx/cgi-bin/ /cgi-bin && exit'

        cd /home/kester/Desktop/images_numbered
        lftp ftp.fatcow.com -e 'cd images_numbered && mput image_*txt && exit'

    D) Verify trouble spots are OK:
        http://www.poresopropongo.mx/card/7735
        http://www.poresopropongo.mx/card/7421


Update FB cache at https://developers.facebook.com/tools/debug/og/object/
