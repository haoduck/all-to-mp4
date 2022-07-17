import ffmpeg #pip3 install ffmpeg-python
import os
import sys

def get_files(path='E:\\xx', rules=['.wmv','.asf','.asx','.rm','. rmvb','.mpg','.mpeg','.mpe','.3gp','.mov','.mp4','.m4v','.avi','.dat','.mkv','.flv','.vob']):
    all = []
    # os.walk是获取所有的目录
    for fpath, dirs, fs in os.walk(path):
        for f in fs:
            filename = os.path.join(fpath, f)
            # 判断是否以"rule"结尾，自定义规则
            for rule in rules:
                if filename.lower().endswith(rule.lower()):
                    all.append(filename)
    return all

def ff(source_name):
    # source_name=r'E:test.mp4'
    bit_rate_best=3670016 #目标码率,源文件大于预设码率就转码
    vcodec='h264' #可以指定硬件编码,通用的是h264(跑CPU),N卡是h264_nvenc,A卡是h264_amf,I卡是h264_qsv,装好驱动才能用.当然,你也可以选择其他如h265等
    try:
        info = ffmpeg.probe(source_name)
        try:
            bit_rate=info['streams'][0]['bit_rate']
        except: #视频流不能获取到码率的情况下则从总码率预估
            bit_rate=str(int(info['format']['bit_rate'])-131072) #总码率-131072(128k)
        print(bit_rate)
        if (int(bit_rate) < bit_rate_best+131072) and (source_name.lower().endswith('.mp4')): #加131072，减少一些收益低的转码
            print('文件:',source_name,'自身码率:',bit_rate,'比目标码率:',bit_rate_best,'低(或接近).跳过')
            return
        elif (int(bit_rate) < bit_rate_best+131072) and (not source_name.lower().endswith('.mp4')): #加131072，减少一些收益低的转码
                print('文件:',source_name,'自身码率:',bit_rate,'比目标码率:',bit_rate_best,'低(或接近).使用原本的码率数值:',bit_rate)
                bit_rate_best=bit_rate

        to_name=os.path.splitext(source_name)[0]+'_lite.mp4'
        while os.path.exists(to_name):
            to_name=os.path.splitext(to_name)[0]+'_1.mp4' #有时有同名不同格式的情况下,在后面加_1,有3个同名文件则会变成_1_1,以此类推
        (
            ffmpeg
            .input(source_name) #ffmpeg -i source_name
            .output(to_name,**{'c:a':'copy','c:v':vcodec,'b:v': str(bit_rate_best)}) #相当于-c:a copy -c:v h264_nvenc -b:v 3670016
            .global_args("-y") #这里的-y就是ffmpeg -y,覆盖已经存在的文件,改为-n则为跳过
            .run(capture_stdout=False)
        )
        os.rename(source_name,source_name+'.ffbak') #源文件添加后缀.ffbak,确认无误后可删除
        os.rename(to_name,to_name.replace('_lite','')) #去掉临时添加的_lite

    except:
        print(source_name,'执行失败')
        if os.path.exists(to_name):
            os.remove(to_name)

def main():
    # path=r'E:\xx'
    path=sys.argv[1]
    try:
        if sys.argv[2] == 'delbak':
            delbak=True
    except:
        delbak=False
    if delbak:
        files=get_files(path,['.ffbak'])
        if files:
            for file in files:
                print('删除此文件:',file)
                os.remove(file)
        else:
            print(path,'未获取到.ffbak文件')
    else:
        files=get_files(path)
        if files:
            for file in files:
                print('执行此文件:',file)
                ff(file)
        else:
            print(path,'未获取到指定的媒体文件')

if __name__ == '__main__':
    # python3 main.py 'E:\xx'
    # python3 main.py 'E:\xx' 'delbak' #删除.ffbak文件
    main()
