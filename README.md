# TheBusinessOfMachineLearning
Code on the Beach 2018 Presentation and content

## Prerequisite
* Docker
* Git

## Start the Presentation
To build the container for the presentation run `bash bin/build_presentation.sh` if you are running the presentation for the first time.  If you are running on the Windows platform execute these commands from within a git bash command prompt

To start the presentation run `bash bin/run_presentation.sh`


## Prepare the Data foir Model Training
Before training the model we first need to download the data.  If you run `bash bin/run_prepare.sh` and you have not downloaded the data set yet you will receive instructions on how to download the data

After the NFL Play by Play 2009-2017.csv file is downloaded and placedin the data directory run `bash bin/run_prepare.sh` to create the NFLPlays2009_2017.psv in the data directory.  This is the file we will train the models on.

## Train the Models

To execute the training pipeline execute `bash bin/run_train.sh`

There are three models that are trained which are all Random Forest models
* Regression Model - Models a continuous variable 
* Multi Class Classification Model - Models a class that has 3 more more possible values
* Binary Classification Model - Models a 0/1 value

## Outputs from Model Training
The model outputs are in the model folder and the data folder.  There is a folder for each model that was trained.

### Data Folder
The data folder contains the cross validation output from each of the models.  This is a csv file that contains the features the model was trained on along with the prediction and the ylabel. The Y column represents the value we are attempting to predict and the YHat is the prediction.

### Model folder
The model folder contains 3 artifacts
* FACTORMAP - A datastructure that contains the mappings of the classification features of the model along with their numerical representation in the model
*  FEATUREMAP - a data structure that contains each of the features of the model along with the 1 based index position each feature belongs in the matrix when we perform a prediction

## Presenting Model as an API

To expose the models as an api endpoint execute `bash bin/run_webserver.sh`.

To exercise the models open Postman and import the codeonthebeach2018.postman_collection.json.

There are three api endpoints
* nfl-regression - The regression model (prediction a continuous value ie numerical)
* nfl-binary classifier - A binary classification model (predicting 1/0)
* nfl-multiclass classifier - A classification model (predicting a label ie string value)

Feel free to change the values in the body of the request and see the predictions change



