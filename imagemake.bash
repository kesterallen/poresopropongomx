7  */6   *   *   *     lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'mirror --verbose=3 --reverse --delete /home/kester/Dropbox/Mosaic\ PNGs/ /images && exit'
30 */6   *   *   *     lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'cd images && find . && exit' >| '/home/kester/Dropbox/Mosaic PNGs/image_list.txt'
35 */6   *   *   *     cd /home/kester/Dropbox/Mosaic\ PNGs && lftp ftp.fatcow.com -u 'poresopropongomx,Newyork1234!' -e 'cd images && put image_list.txt && exit'
