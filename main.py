import ffmpeg #pip3 install ffmpeg-python
import os
import sys

def get_files(path='E:\\xx', rules=['.mp4','.mov','.avi','.flv','rmvb']):
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
    bit_rate_best=3584 #目标码率,设置3584表示3584k,源文件大于预设码率就转码
    vcodec='h264_nvenc' #可以指定硬件编码,通用的是h264(跑CPU),N卡是h264_nvenc,A卡是h264_amf,I卡是h264_qsv,装好驱动才能用
    try:
        info = ffmpeg.probe(source_name)
        bit_rate=info['streams'][0]['bit_rate']
        print(bit_rate)
        if int(bit_rate) > bit_rate_best:
            to_name=os.path.splitext(source_name)[0]+'_lite.mp4'
            while os.path.exists(to_name):
                to_name=os.path.splitext(to_name)[0]+'_1.mp4'
            (
                ffmpeg
                .input(source_name) #ffmpeg -i source_name
                .output(to_name,**{'c:a':'copy','c:v':vcodec,'b:v': str(bit_rate_best)+'k'}) #相当于-c:a copy -c:v h264_nvenc -b:v 3584k
                .global_args("-y") #这里的-y就是ffmpeg -y,覆盖已经存在的文件,改为-n则为跳过
                .run(capture_stdout=True)
            )
            os.rename(source_name,source_name+'.bak') #源文件添加后缀.bak,确认无误后可删除
            os.rename(to_name,to_name.replace('_lite','')) #去掉临时添加的_lite
        else:
            print('文件:',source_name,'自身码率:',bit_rate,'比目标码率:',bit_rate_best,'低。跳过')
    except:
        print(source_name,'执行失败')

def main():
    # path=r'E:\xx'
    path=sys.argv[1]
    files=get_files(path)
    if files:
        for file in files:
            print('执行此文件:',file)
            ff(file)
    else:
        print(path,'未获取到指定的媒体文件')

if __name__ == '__main__':
    main()
