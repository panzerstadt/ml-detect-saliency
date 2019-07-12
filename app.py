

def main():
    from tools.convert_video.convert_video import preprocess_video, postprocess_video
    from tools.saliency_segment.main import process_saliency

    print('preprocessing video(s)\n')
    preprocess_video()
    print('calculating saliency(s)\n')
    process_saliency()
    print('postprocessing video(s)\n')
    postprocess_video()


if __name__ == '__main__':
    main()