7  */6   *   *   *     lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'mirror --verbose=3 --reverse --delete /home/kester/Dropbox/Mosaic\ PNGs/ /images && exit'
30 */6   *   *   *     lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'cd images && find . && exit' | perl -anle 'print substr($_, 2)' >| '/home/kester/Dropbox/Mosaic PNGs/image_list.txt'
32 */6   *   *   *     ls /home/kester/Dropbox/Mosaic\ PNGs/*.{jpg,jpeg,png} | wc -l >| '/home/kester/Dropbox/Mosaic PNGs/image_count.txt'
35 */6   *   *   *     cd /home/kester/Dropbox/Mosaic\ PNGs && lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'cd images && mput image*.txt && exit'
