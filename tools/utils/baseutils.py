import os

def get_filepath(filepath_with_extension, debug=False):
    test = filepath_with_extension[0]
    if not test == '/':
        filepath_with_extension = '/' + filepath_with_extension
    if test == '.':
        filepath_with_extension = filepath_with_extension[2:]
    if debug: print('starting filepath', filepath_with_extension)

    try:
        with open(filepath_with_extension): pass
        return filepath_with_extension
    except FileNotFoundError:
        try:
            fp0 = '.' + filepath_with_extension
            if debug: print('fp0', fp0)
            with open(fp0): pass
            return fp0
        except FileNotFoundError:
            try:
                fp1 = '..' + filepath_with_extension
                if debug: print('fp1', fp1)
                with open(fp1): pass
                return fp1
            except FileNotFoundError:
                try:
                    fp2 = '../..' + filepath_with_extension
                    if debug: print('fp2', fp2)
                    with open(fp2): pass
                    return fp2
                except FileNotFoundError:
                    try:
                        fp3 = '../../..' + filepath_with_extension
                        if debug: print('fp3', fp3)
                        with open(fp3): pass
                        return fp3
                    except:
                        print('current workingdir: ', os.getcwd())
                        raise SystemError("file not found by traversing backwards 3 folders")


def get_directory(directory, debug=False):
    d = lambda x: os.path.isdir(x)
    if debug: print(directory)
    if d(directory):
        return directory
    else:
        dir0 = '.' + directory
        if d(dir0):
            print('returning: ', dir0)
            return dir0
        else:
            dir1 = '..' + directory
            if d(dir1):
                print('returning: ', dir1)
                return dir1
            else:
                dir2 = '../..' + directory
                if d(dir2):
                    print('returning: ', dir2)
                    return dir2
                else:
                    dir3 = '../../..' + directory
                    if d(dir3):
                        print('returning: ', dir3)
                        return dir3
                    else:
                        print(os.getcwd())
                        raise SystemError("directory not found by traversing 3 folders backwards")


def ensure_folder(folder_path, debug=False):
    if not os.path.isdir(folder_path):
        print('making new folder!')
        os.mkdir(folder_path)
        return folder_path
    else:
        return folder_path


def sort_filenames(filepaths, split_keyword='frame', reverse=False):
    import os

    def get_keys(filepath):

        temp = os.path.basename(filepath)
        temp = os.path.splitext(temp)

        temp = temp[0].split(split_keyword)
        for kw in temp:
            try:
                kw = int(kw)
                return kw
            except:
                pass
        return 0

    output = sorted(filepaths, key=get_keys, reverse=reverse)
    return output

