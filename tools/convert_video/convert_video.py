import cv2, os, json
from tools.utils.baseutils import get_directory, sort_filenames, ensure_folder
from collections import defaultdict

"""
https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames
"""

# input file
input_video_filepath = 'sewing.mp4'

video_framerates = {}


def convert_video_to_frames(input_filepath, output_folder, skip_preprocessed=True, debug=False):
    if len(input_filepath) == 0:
        input_filepath = input_video_filepath
    vidcap = cv2.VideoCapture(input_filepath)

    def get_framerate():
        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

        if int(major_ver) < 3:
            fps = vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
            print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
        else:
            fps = vidcap.get(cv2.CAP_PROP_FPS)
            print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))

        return fps


    video_name = os.path.dirname(output_folder).split('/')[-1]
    video_framerates[video_name] = get_framerate()

    # folder name
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    if skip_preprocessed:
        t = list(os.walk(output_folder))
        if len(t[0][-1]) > 0:
            print(t[0][-1])
            print('found previous frames, skipping video conversion. if you want to overwrite, set skip_preprocessed=False')
            return

    success,image = vidcap.read()
    count = 0

    print('converting {} to frames...'.format(input_filepath))
    while success:
        output_path = os.path.join(output_folder, "frame%d.jpg" % count)
        cv2.imwrite(output_path, image)     # save frame as JPEG file
        success,image = vidcap.read()
        if debug: print('Read a new frame: ', success)
        count += 1
    print('complete!')


def preprocess_video(input_folder_path='./data/', skip_preprocessed=True):
    input_video_directory = input_folder_path

    input_video_directory = get_directory(input_video_directory, debug=True)
    video_paths = [dataset for dataset in os.listdir(input_video_directory + 'video/') if
                   os.path.isdir(input_video_directory + 'video/')]

    video_paths = [v for v in video_paths if not v[0] == '.']

    video_fullpaths = []
    frames_dirs = []
    for v in video_paths:
        v_fullpath = os.path.join(input_video_directory, 'video/', v)
        f_dir = os.path.join(input_video_directory, 'frames/' + os.path.splitext(v)[0] + '/')

        video_fullpaths.append(v_fullpath)
        frames_dirs.append(f_dir)

    video_tuple = zip(video_fullpaths, frames_dirs)

    [convert_video_to_frames(input_filepath=t[0], output_folder=t[1], skip_preprocessed=skip_preprocessed) for t in video_tuple]


def convert_frames_to_video(frames_list_in, output_filename='output', framerate=None, sort=True, debug=False):
    if sort:
        frames_list_in = sort_filenames(frames_list_in, split_keyword='frame')

    if debug: print(frames_list_in[:10])

    images = [cv2.imread(file) for file in frames_list_in]

    if debug: print(images)

    if not framerate:
        print("using default framerate of 23.976.")
        framerate = 23.976

    height, width, layers = images[0].shape
    out = cv2.VideoWriter(output_filename + ".mp4", cv2.VideoWriter_fourcc(*"mp4v"), framerate, (width, height))

    for f in images:
        out.write(f)
    out.release()


def postprocess_video(input_folder_path='./data/frames/', processed_frames_path='./results/', output_folder='./results/', name_filter=None, skip_postprocessed=True, debug=False):

    def original_folders_and_name(input_folder_path):
        # getting the name from input folder
        t = list(os.walk(input_folder_path))
        original_frames = t[0]
        original_folders = [os.path.join(original_frames[0], x) for x in original_frames[1] if x != 'video']

        video_names = original_frames[1]

        return original_folders, video_names

    def processed_folders(processed_frames_path):

        t = list(os.walk(processed_frames_path))
        processed_frames = t[0]

        processed_folders = [os.path.join(processed_frames[0], x) for x in processed_frames[1] if x != 'video']

        static_saliency_fp = [f for f in processed_folders if 'static' in f][0]
        t = list(os.walk(static_saliency_fp))
        static_saliency_fp = t[0]
        static_saliency_folders = [os.path.join(static_saliency_fp[0], x) for x in static_saliency_fp[1] if x != 'video']

        dynamic_saliency_fp = [f for f in processed_folders if 'dynamic' in f][0]
        t = list(os.walk(dynamic_saliency_fp))
        dynamic_saliency_fp = t[0]
        dynamic_saliency_folders = [os.path.join(dynamic_saliency_fp[0], x) for x in dynamic_saliency_fp[1] if x != 'video']

        return static_saliency_folders, dynamic_saliency_folders


    original_f, v_names = original_folders_and_name(input_folder_path)
    static_f, dynamic_f = processed_folders(processed_frames_path)

    if debug:
        print(original_f)
        print(v_names)
        print(static_f)
        print(dynamic_f)

    # check if dynamic saliency matches

    def build_filepath_dict():
        def get_frames_and_length(f):
            t = list(os.walk(f))
            frames = t[0]

            frames_fullpath = [os.path.join(frames[0], f) for f in frames[-1]]
            frames_fullpath = sort_filenames(frames_fullpath)
            num_of_frames = len(frames_fullpath)

            return frames_fullpath, num_of_frames

        filepaths_dict = {}
        for i, f in enumerate(original_f):
            print('building original set for {}'.format(f))
            frames, length = get_frames_and_length(f)

            filepaths_dict[v_names[i]] = {}

            filepaths_dict[v_names[i]]['original'] =  {
                "frames": frames,
                "length": length
            }

        for i, f in enumerate(static_f):
            f_name = os.path.basename(f)
            for k in filepaths_dict.keys():
                if k == f_name:

                    print('building static saliency set for {}'.format(f))
                    frames, length = get_frames_and_length(f)

                    filepaths_dict[f_name]['static'] = {
                        "frames": frames,
                        "length": length
                    }

        for i, f in enumerate(dynamic_f):
            f_name = os.path.basename(f)
            for k in filepaths_dict.keys():
                if k == f_name:
                    print('building dynamic saliency set for {}'.format(f))
                    frames, length = get_frames_and_length(f)

                    filepaths_dict[f_name]['dynamic'] = {
                        "frames": frames,
                        "length": length
                    }

        return filepaths_dict

    all_frames = build_filepath_dict()

    with open('.temp.json', 'w') as j:
        json.dump(all_frames, j, indent=4, ensure_ascii=False)

    def run_convert(frames_dataset=all_frames, output_folder=output_folder, type='static', debug=False):

        def is_hidden(filepath):
            import os
            t = os.path.basename(filepath)
            t = os.path.splitext(t)[0]

            if t[0] == '.':
                return True
            else:
                return False

        for k, d in frames_dataset.items():
            video_name = k
            frames_to_convert = d[type]['frames']

            # convert only selected videos
            if name_filter:
                if not video_name == name_filter:
                    continue

            output_f = os.path.join(output_folder, 'video/')
            output_f = ensure_folder(output_f)

            if debug:
                print('output folder: ', output_f)
                print('video name: ', video_name)

            if skip_postprocessed:
                try:
                    t = list(os.walk(output_f))
                    if len(t[0][-1]) > 0:
                        if any(video_name in x for x in t[0][-1]):
                            print(t[0][-1])
                            print(
                                'found previous frames, skipping video conversion. if you want to overwrite, set skip_preprocessed=False')
                            continue
                except:
                    pass

            cleaned_input = [f for f in frames_to_convert if not is_hidden(f)]  # cleans hidden files
            sorted_input = sort_filenames(cleaned_input)

            output_filename = os.path.join(output_f, video_name)

            print("converting frames:")
            print("from frames: {}".format(sorted_input[:10]))
            print("to video: {}".format(output_filename + (".mp4")))
            print("framerate: {}".format(video_framerates[video_name]))

            convert_frames_to_video(sorted_input, output_filename=output_filename, framerate=video_framerates[video_name])

    print('\nconverting:')
    run_convert(frames_dataset=all_frames, type='static')
    print('complete!')







if __name__ == '__main__':
    # input_filename = input('specify video filepath here, or press ENTER to test run using a default file: ')
    # convert_video_to_frames(input_filename)

    postprocess_video(input_folder_path='./frames')

