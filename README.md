
# ProSemanticSegmentation

A deep-learning implementation for semantic segmentation of remote sensing data. This flowchart demonstrates the sequence of actions:
![alt tag](https://raw.githubusercontent.com/xxsmario/ProSemanticSegmentation/master/docs/workflow.png)

## Workflow Execution Process (For Forest toy data)
Download the Forest toy data from the link https://storage.googleapis.com/nextgenmap-dataset/dl-semantic-segmentation/forest_toy.zip and follow the instructions outlined below (...Or if you're in a rush, run the whole process by executing run_forest_toy.sh):
1. Initial step is to standardize the two images, one to train the model and another for classification:
```sh
$ ./standardize_imgs.py -n 0 -b 1 2 3 4 -i forest_toy/raw_data/mosaic_201709.tif forest_toy/raw_data/mosaic_201801.tif -o forest_toy/stand_data
```
2. Next, stack the standardized image and the forest atlas (i.e. the reference data):
```sh
$ ./stack_imgs.py -i forest_toy/stand_data/mosaic_201709_stand.tif -r forest_toy/raw_data/forest_201709.tif -o forest_toy/stand_data/forest_201709_model_input.vrt
```