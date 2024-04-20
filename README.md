
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
3. Then generate the chips (i.e. a set of pixels with regular squared size) without augmenting data ([see usages](#usages)):
```sh
$ ./generate_chips.py -f 0,0 -r -l -u -i forest_toy/stand_data/forest_201709_model_input.vrt -o forest_toy/chips
```
4. The next step involves training a U-net model, for 20 epochs, using default hyperparameters ([see usages](#usages)):
```sh
$ ./train_model.py -e 20 -i forest_toy/chips -o forest_toy/model/
```
* Monitor the training process using tensorboard:
```sh
$ tensorboard --logdir=forest_toy/model/
```
5. Following training, evaluate the built model:
```sh
$ ./evaluate_model.py -m forest_toy/model
```
6. Finally, classify the other image:
```sh
$ ./classify_imgs.py -m forest_toy/model -i forest_toy/raw_data/mosaic_201801.tif -o forest_toy/result
```
* Review the classification outcome, forest_toy/result/mosaic_201801_pred.tif, on [QGIS](https://www.qgis.org):
For detailed explanation on usage, refer to the provided documentation under header **Usage** for each of the functions.