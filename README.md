<div align="center">
    <img src="./docs/images/logo_v9.png" alt="logo" width="450"/>
</div>

**soundscape_IR** is a python-based toolbox of soundscape information retrieval, aiming to assist in the analysis of soundscape recordings. 
The toolbox is primarily desgined for: (1) visualization of soundscape dynamics (based on the MATLAB package [Soundscape Viewer](https://github.com/schonkopf/soundscape-viewer)) and (2) audio source separation.

See https://meil-brcas-org.github.io/V1.1/index.html for technical documentation and more examples.

[![DOI](https://zenodo.org/badge/485700854.svg)](https://zenodo.org/badge/latestdoi/485700854)

## Installation
Dependencies:
- Python>=3.7
- numpy>=1.22
- pandas>=1.3.5
- audioread>=2.1.9
- librosa>=0.8.1
- scikit-learn>=1.0.2
- scipy>=1.7.3
- matplotlib>=3.2.2
- plotly>=5.5.0

To install **soundscape_IR**, clone the repository in your Python environment.
```bash
# Clone soundscape_IR from GitHub @meil-brcas-org
git clone https://github.com/meil-brcas-org/soundscape_IR.git
```
Then, install the [requirements.txt](https://github.com/meil-brcas-org/soundscape_IR/blob/master/requirements.txt) in the package folder for installing required packages.
```bash
# Install required packages
cd soundscape_IR
pip install -r requirements.txt
```

## Quick start
<div align="center">
<img src="./docs/images/workflow_v14.png" width="1000"/>
</div>

<div>
   <a href="https://colab.research.google.com/drive/1xPJR2LbC-5hOGK5d25u6_6zmSznJ3kHo?usp=sharing"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
</div></br>

<details open>
<summary>Audio visualization</summary>

**soundscape_IR** provides a function ```audio_visualization``` to transform an audio into a spectrogram on the hertz or mel scale. It also enables the use of Welch’s averaging method and spectrogram prewhitening in noise reduction. This example uses a short audio clip of sika deer calls and insect calls to demonstrate the ecoacoustic application of source separation.
 
```python
from soundscape_IR.soundscape_viewer import audio_visualization

# Define spectrogram parameters
sound_train = audio_visualization(filename='case1_train.wav', path='./data/wav/', offset_read=0, duration_read=15,
                                  FFT_size=512, time_resolution=0.1, prewhiten_percent=10, f_range=[0,8000])
```
<img src="./docs/images/fp_1.png" alt="fp_1.png" width="650"/>
</details>

<details open>
<summary>Model training</summary>
    
After preparing the training spectrogram, we can train a model with ```source_separation```. NMF learns a set of basis functions to reconstruct the training spectrogram. In **soundscape_IR**, we can apply PC-NMF to separate the basis functions into two groups according to their source-specific periodicity. In this example, one group of basis funcitons is associated with deer call (mainly < 4 kHz) and another group is associated with noise (mainly > 3.5 kHz). Save the model for further applications.

```python
from soundscape_IR.soundscape_viewer import source_separation

# Define model parameters
model=source_separation(feature_length=30, basis_num=10)

# Feature learning
model.learn_feature(input_data=sound_train.data, f=sound_train.f, method='PCNMF')

# Plot the basis functions of two sound source
model.plot_nmf(plot_type='W', source=1)
model.plot_nmf(plot_type='W', source=2)

# Save the model
model.save_model(filename='./data/model/deer_model.mat')
```
<img src="./docs/images/fp_2.png" alt="fp_2.png" width="650"/> 
<img src="./docs/images/fp_3.png" alt="fp_3.png" width="650"/>
</details>

<details open>
<summary>Deployment and spectrogram reconstruction</summary>   

Generate another spectrogram for testing the source separation model.

```python
# Prepare a spectrogram
sound_predict=audio_visualization(filename='case1_predict.wav', path='./data/wav/', offset_read=30, duration_read=15,
                                    FFT_size=512, time_resolution=0.1, prewhiten_percent=10, f_range=[0,8000])
```   
<img src="./docs/images/fp_4.png" alt="fp_4.png" width="650"/>
  
Load the saved model and perform source separation. After the prediction procedure, plot the reconstructed spectrograms to evaluate the separation of deer calls and noise.
    
```python
# Deploy the model
model=source_separation()
model.load_model(filename='./data/model/deer_model.mat')
model.prediction(input_data=sound_predict.data, f=sound_predict.f)

# View individual reconstructed spectrogram
model.plot_nmf(plot_type = 'separation', source = 1)
model.plot_nmf(plot_type = 'separation', source = 2)
```  
<img src="./docs/images/fp_5.png" alt="fp_5.png" width="650"/>
<img src="./docs/images/fp_6.png" alt="fp_6.png" width="650"/>
</details>

<details open>
<summary>Presence detection</summary>
    
With the reconstructed spectrogram, we can use the function ```spectrogram_detection``` to detect the presence of target signals (e.g., deer calls). This function will generate a txt file contains the beginning time, ending time, minimum frequency, and maximum frequency of each detected call. Explore the detection result in [Raven software](https://ravensoundsoftware.com/).
    
```python
from soundscape_IR.soundscape_viewer import spectrogram_detection

# Choose the source for signal detection
source_num=2
    
# Define the detection parameters
sp=spectrogram_detection(model.separation[source_num-1], model.f, threshold=5.5, smooth=1, minimum_interval=0.5, 
                           filename='deer_detection.txt', path='./data/txt/')
```
<img src="./docs/images/fp_7.png" alt="fp_7.png" width="650"/>
</details>

<details open>
<summary>More tutorials</summary>
    
- [Demo of audio source separation - Detecting deer calls from tropical forest soundscapes](./docs/tutorials/Demo_of_soundscape_IR_Case_study_I.ipynb)
- [Demo of audio source separation - Learning the diversity of underwater sounds from subtropical estuary soundscapes](./docs/tutorials/Demo_of_soundscape_IR_Case_study_II.ipynb)
- [Demo of batch processing - Automatically analyzing a large number of soundscape recordings](./docs/tutorials/Demo_Batch_processing.ipynb)
- [Demo of Soundscape Viewer - Investigating soundscape dynamics via visualization of long-duration recordings, blind source separation, and clustering](./docs/tutorials/Demo_of_soundscape_information_retrieval.ipynb)
    
</details>

## Currently ongoing developments
- [ ] Soundscape spatial analysis
- [ ] Plotly-based interactive plots
    
## Future works
- [ ] GPU accelaration

## Citing this work

If you find this package useful in your research, we would appreciate citations to:
    
- Sun, Y-J, Yen, S-C, & Lin, T-H (2022). soundscape_IR: A source separation toolbox for exploring acoustic diversity in soundscapes. Methods in Ecology and Evolution, 13: 2347-2355. https://doi.org/10.1111/2041-210X.13960

## Bugs report and suggestions 
If you encounter any bug or issue, please contact Dr. Tzu-Hao Lin via schonkopf@gmail.com. Suggestions are also appreciated!

## About the team
**Marine Ecoacoustics and Informatics Lab (MEIL)**</br>
Led by Dr. Tzu-Hao Lin, the MEIL investigates the applications of ecological informatics in biodiversity monitoring and conservation management. If you're interested in our work, please check our [website](https://meil.biodiv.tw/home) or follow us on [facebook](https://www.facebook.com/meil.brcas).
