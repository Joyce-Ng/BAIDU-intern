#!/bin/bash
#下载原结果页XML数据
url_pre='http://nj02-wd-knowledge47-ssd1l.nj02.baidu.com:8086/jingdian/output/jingdianjieguoye/jingdian_jingdianjieguoye_00'
url_suf='.xml'
for i in `seq -w 599`
do
    wget $url_pre$i$url_suf
done
mv jingdian_jingdianjieguoye_* output/
#字符串替换，生成新的结果页XML数据
cd output
sed -i "s/resource_id=4491/resource_id=4616/g" `grep resource_id=4491 -rl ./`
for j in `seq -w 599`
do
    filename='jingdian_jingdianjieguoye_00'$j'.xml'
    for var in `grep "http://image.baidu.com/search/wiseala?tn=wiseala&amp;ie=utf8&amp;word=" $filename`
    do
        #取出word,拼接新的图片情景页
        varL=${var%'</imgUrl>'*}
        varR=${varL#*'word='}
        word=${varR%'&amp;fr=alawise'*}
        if [ -z "$word" ]
        then
            echo 'empty'
        else
	    old_str='word='$word'\&mod=0\&tn=normal\&pd=jingdian_comment\&actname=common_img_view\&sf_resource_id=33285'
	    new_str='openapi=1\&dspName=iphone\&from_sf=1\&pd=jingdian_detail\&resource_id=4617\&ms=1\&hide=1\&apitn=tangram\&top%7B%22sfhs%22%3A2%7D\&ext=%7B%22sf_tab_name%22%3A%22%E5%9B%BE%E7%89%87%22%7D\&word='${word}'\&title='${word}
	    sed -i "s/$old_str/$new_str/g" `grep $old_str -rl ./`
        fi
    done
done
