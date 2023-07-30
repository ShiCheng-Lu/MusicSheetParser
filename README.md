MusicSheetParser

dataset from https://doi.org/10.21256/zhaw-20647

parser:
1. extract staff and bars using image processing techniques with OpenCV
2. use FasterRCNN image object detection on each bar
3. process labels by their BBoxes and extract individual note pitches and durations

![sample](sample.png)
