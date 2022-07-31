---
title: Video Database
created: 2022-05-05T09:13:55+08:00
modified: 2022-07-21T16:05:26+08:00
---

# Video Database For Video Generation

video object tracking and segmentation unified framework:
https://github.com/MasterBin-IIAU/Unicorn

video object segmentation handle long video with ease:
https://github.com/hkchengrex/XMem

when removing video watermarks, remember to ease in/out. that is said, do not stop blurring immediately after the end mark. instead, extend the blur time and decrease blur level incrementally. also, the blur ease-in is needed for the start mark, blur ahead of the start mark and ease in incrementally.

descriptive information generation from video/image:

https://github.com/BAAI-WuDao/CogView
https://github.com/BAAI-WuDao/BriVL
https://github.com/PaddlePaddle/PaddleVideo/blob/develop/docs/zh-CN/install.md

video understanding/captioning:

https://github.com/rohit-gupta/Video2Language
https://github.com/byeongjokim/Automatic-Baseball-Commentary-Generation-Using-DeepLearning
https://github.com/shhdSU/Image_Captioning_DeepLearning
https://github.com/jayleicn/recurrent-transformer
https://github.com/terry-r123/Awesome-Captioning
https://github.com/vijayvee/video-captioning
https://github.com/scopeInfinity/Video2Description
https://github.com/xiadingZ/video-caption.pytorch
https://github.com/YehLi/xmodaler
https://github.com/sujiongming/awesome-video-understanding

action recognition:

https://github.com/mit-han-lab/temporal-shift-module
https://github.com/yjxiong/temporal-segment-networks
https://github.com/yjxiong/tsn-pytorch
https://github.com/open-mmlab/mmaction
https://github.com/jinwchoi/awesome-action-recognition

The data remaining only have texts, danmaku, likes, titles, intros, comments, tags, image/video analysis results(short description). You can only generate video from generated metadata or given rules. Find similar words, similar danmaku, similar features, comments or the inverse, according to the selected topic and main idea.

Analyze video when downloaded, mark its highlights, analyze texts and danmaku. Get video segments and audio segments.

Collect pictures/videos with given rules, namely finding the head of somebody, with how many likes, keywords.

Split audio and grab the main speaker. clone the voice and perhaps changes the gender.

Split video and do human/image segmentation if human/target is found. put it onto another human/target's background masking the original human, with similar areas and movements.

Analyze video with off-topic(offline) and of-topic(online) sources.

Remove watermark according to username.

Generate danmaku and generate video accordingly. Generate texts and generate video accordingly. Doing faceswap, talking head and human/image segmentation accordingly.
