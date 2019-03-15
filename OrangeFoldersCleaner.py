#!/usr/bin/python
#coding: utf-8

import os, os.path, time, ctypes, zipfile


# Квоты по умолчанию (безопасные)
save_quotes = {
    'quota_by_days' : 'no',
    'days' : 365,
    'extensions' : ['bak', 'diff_bak'],
    'absolute_ways' : 'yes',
    'save_original_files' : 'yes',
    'paths' : []
    }

TYPES = {'kb' : 1, 'mb' : 2, 'gb' : 3, 'tb' : 4}
FILE_CFG = 'OFC.cfg'


def del_qommas(string):
    l = len(string.strip())
    pos = string.find("'")
    return str(string[pos+1:l-1].strip())


def get_bytes_in_type(bytes, type):
    bytes /= 1024 ** int(TYPES[type])
    return float('{:.2f}'.format(bytes))


def get_configure(file_cfg):
    quotes = {
                'quota_by_days': '',
                'days': '',
                'extensions': [],
                'absolute_ways': '',
                'save_original_files': '',
                'paths': []
            }
    check_qbd = False
    check_aw = False
    check_sof = False
    check_e = False

    try:
        with open(file_cfg, 'r') as fileCfg:
            for line in fileCfg:

                if not line.count('=='):
                    if line.count('dir') > 0:
                        quotes['paths'].append(del_qommas(line.strip()))
                        try:
                            pass #check path for exist
                        except:
                            pass #err path is not exist. Exit

                    if line.count('quota_by_days') > 0 and line.count('yes') > 0:
                        l = fileCfg.readline()
                        quotes['quota_by_days'] = 'yes'
                        quotes['days'] = int(del_qommas(l))
                        check_qbd = True
                    elif not check_qbd:
                        quotes['quota_by_days'] = 'no'

                    if line.count('absolute_ways') > 0 and line.count('no') > 0:
                        quotes['absolute_ways'] = 'no'
                        check_aw = True
                    elif not check_aw:
                        quotes['absolute_ways'] = 'yes'

                    if line.count('save_original_files') > 0 and line.count('no') > 0:
                        quotes['save_original_files'] = 'no'
                        check_sof = True
                    elif not check_sof:
                        quotes['save_original_files'] = 'yes'

                    if line.count('extensions') > 0 and line.count("'") > 0:
                        quotes['extensions'] = []
                        i = 0
                        string = line
                        while len(string) > 1 and string.count("'") and i < 10000:
                            pos = string.find("'")
                            string = string[pos + 1:len(string)]
                            pos = string.find("'")
                            if string[0:pos] != '':
                                quotes['extensions'].append(string[0:pos])
                            string = string[pos + 1:len(string)]
                            i += 1
                        check_e = True
                    elif not check_e:
                        pass # err ext taken. Exit
        fileCfg.close()

        if not (check_qbd and check_aw and check_sof and check_e):
            pass #err in cfg file. Exit

        return quotes
    except:
        print("Looks like no file Back_Ops.cfg in the current folder.\nCurrent folder is:", os.getcwd(),
              "\nScript stopped.")
        exit(1)


def get_list_of_files(mainDirList):
    listFiles = []
    for curDir in mainDirList:
        if os.path.exists(curDir):
            for item in os.walk(curDir):
                listFiles.append(item)
    return listFiles


def delete_by_days(listFiles, days): # not tested
    etalon = time.time()
    #curListFiles = listFiles
    for lf in listFiles:

        curFilePeriod = (etalon - os.path.getctime(lf)) / 86400
        if not zipfile.is_zipfile(lf) and lf.endswith('.zip'):
            print('corrupted ZIP!')

        #z = zipfile.ZipFile('xml_healer.zip', 'r')

        if curFilePeriod > days:
            print(file_mime_type(lf))











            deleted = listFiles.pop()
            if os.path.isfile(str(deleted)):
                os.remove(str(deleted))
            else:
                print('File is not exist: ', deleted)

    return listFiles


def get_free_space(dirname):

    free_bytes = ctypes.c_ulonglong(0)
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))

    return free_bytes.value


def zip_files(curDir, extensions, ways, save):

    listFiles = [f for f in os.listdir(curDir) if os.path.isfile(os.path.join(curDir,f))]

    for curFile in listFiles:
        file_extension = os.path.splitext(curFile)[1]
        if os.path.getsize(os.path.join(curDir, curFile)) < get_free_space(curDir):
            if file_extension[1:len(file_extension)] in extensions:
                if curFile.endswith('.bak'):
                    zipfilename = curFile[0:curFile.find('.')] + '.zip'
                elif curFile.endswith('.diff_bak'):
                    zipfilename = curFile[0:curFile.find('.')] + '_diff.zip'
                print(curFile, ' - ', zipfilename)
                start = time.time()

                jungle_zip = zipfile.ZipFile(os.path.join(curDir, zipfilename), 'w', allowZip64=True)
                if ways == 'yes':
                    jungle_zip.write(os.path.join(curDir, curFile), zipfilename, compress_type=zipfile.ZIP_BZIP2)
                else:
                    jungle_zip.write(os.path.join(curDir, curFile), compress_type=zipfile.ZIP_BZIP2)
                jungle_zip.close()

                end = time.time()
                print(float('{:.2f}'.format(end - start)), 'sec')
                if save == 'no':
                    if os.path.exists(os.path.join(curDir, curFile)):
                        os.remove(os.path.join(curDir, curFile))
                    else:
                        print("The file ", os.path.join(curDir, curFile), " does not exist")

def main():
    conf = get_configure(FILE_CFG)
    print(conf)
    mainDirList = get_list_of_files(conf['paths'])
    print(conf)
    for curDir in mainDirList:
        curDirFilesList =[]
        for curFile in curDir[2]:
            if os.path.isfile(os.path.join(curDir[0],curFile)):
                curDirFilesList.append(os.path.join(curDir[0],curFile))

        if conf['quota_by_days'] == 'yes':
            curDirFilesList = delete_by_days(curDirFilesList, conf['days'])

        #zip_files(curDir[0], conf['extensions'], conf['absolute_ways'], conf['save_original_files'])

    exit(0)

if __name__ == '__main__':
    main()