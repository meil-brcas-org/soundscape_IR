"""
Soundscape information retrieval
Author: Tzu-Hao Harry Lin (schonkopf@gmail.com)
"""

import numpy as np

class gdrive_handle:
    def __init__(self, folder_id):
        get_ipython().system('pip install -U -q PyDrive')
        from pydrive.auth import GoogleAuth
        from pydrive.drive import GoogleDrive
        from google.colab import auth
        from oauth2client.client import GoogleCredentials
        
        self.folder_id=folder_id
        auth.authenticate_user()
        gauth = GoogleAuth()
        gauth.credentials = GoogleCredentials.get_application_default()
        self.Gdrive = GoogleDrive(gauth)
        print('Now establishing link to Google drive.')
    
    def upload(self, filename):
        upload_ = self.Gdrive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": self.folder_id}], 'title': filename})
        upload_.SetContentFile(filename)
        upload_.Upload()
        print('Successifully upload to Google drive')
    
    def list_query(self, file_extension):
        location_cmd="title contains '"+file_extension+"' and '"+self.folder_id+"' in parents and trashed=false"
        self.file_list = self.Gdrive.ListFile({'q': location_cmd}).GetList()
    
class save_parameters:
    def __init__(self):
        self.platform='python'
    
    def pcnmf(self, f, W, W_cluster, source_num, feature_length, sparseness, basis_num):
        self.f=f
        self.W=W
        self.W_cluster=W_cluster
        self.k=source_num
        self.time_frame=feature_length
        self.sparseness=sparseness
        self.basis_num=basis_num

    def LTS_Result(self, LTS_median, LTS_mean, f, link):
        self.LTS_median = LTS_median
        self.LTS_mean = LTS_mean
        self.f = f
        self.link = link

    def LTS_Parameters(self, FFT_size, overlap, sensitivity, sampling_freq, channel):
        self.FFT_size=FFT_size
        self.overlap=overlap 
        self.sensitivity=sensitivity 
        self.sampling_freq=sampling_freq 
        self.channel=channel

class audio_visualization:
    def __init__(self, filename, duration_read=None, fft_size=512, window_overlap=0.5):
        import audioread
        import librosa
        import librosa.display
        from IPython.display import Audio
        import matplotlib.pyplot as plt
        import os
        
        # Get the sampling frequency
        with audioread.audio_open(os.getcwd()+'/'+filename) as temp:
            sr=temp.samplerate
            
        # load audio data
        x, sr = librosa.load(filename, sr=sr, duration=duration_read)
        
        # plot the waveform
        plt.figure(figsize=(14, 10))
        ax1 = plt.subplot(2, 1, 1)
        librosa.display.waveplot(x, sr=sr)
        
        # run FFT and make a log-magnitude spectrogram
        X = librosa.core.stft(x, n_fft=fft_size, hop_length=int(fft_size*(1-window_overlap)), win_length=fft_size)
        data = librosa.amplitude_to_db(abs(X))
        
        # plot the spectrogram
        plt.subplot(2, 1, 2, sharex=ax1)
        librosa.display.specshow(data, x_axis='time', y_axis='hz',  sr=sr, hop_length=int(fft_size*(1-window_overlap)))
        
        # make an interactive interface for the audio 
        Audio(x,rate=sr)
        
class matrix_operation:
    def __init__(self, header=[]):
        self.header=header
    
    def gap_fill(self, time_vec, data):
        # fill the gaps in a time series
        temp = np.argsort(time_vec)
        time_vec=time_vec[temp]
        if data.ndim>1:
            output=data[temp,:]
        else:
            output=data[temp]
        
        resolution=np.round((time_vec[1]-time_vec[0])*24*3600)
        n_time_vec=np.arange(np.floor(np.min(time_vec))*24*3600, 
                             np.ceil(np.max(time_vec))*24*3600,resolution)/24/3600

        if data.ndim>1:
            save_result=np.zeros((n_time_vec.size, data.shape[1]+1))
        else:
            save_result=np.zeros((n_time_vec.size, 2))

        save_result[:,0]=n_time_vec-693960
        segment_list=np.round(np.diff(time_vec*24*3600)/resolution)
        split_point=np.vstack((np.concatenate(([0],np.where(segment_list!=1)[0]+1)),
                               np.concatenate((np.where(segment_list!=1)[0],[time_vec.size-1]))))

        for run in np.arange(split_point.shape[1]):
            i=np.argmin(np.abs(n_time_vec-time_vec[split_point[0,run]]))
            if data.ndim>1:
                save_result[np.arange(i,i+np.diff(split_point[:,run])+1),1:]=output[np.arange(split_point[0,run], split_point[1,run]+1),:]
            else:
                save_result[np.arange(i,i+np.diff(split_point[:,run])+1),1]=output[np.arange(split_point[0,run], split_point[1,run]+1)]
        
        return save_result

    def spectral_variation(self, input_data, f, percentile=[], hour_selection=[], month_selection=[]):
        import pandas as pd
        
        if not percentile:
            percentile=np.arange(1,100)
        
        time_vec=input_data[:,0]
        input_data=input_data[:,1:]

        if len(hour_selection)==1:
            hour_selection=np.concatenate((np.array(hour_selection), np.array(hour_selection)+1))
        hour=24*(time_vec-np.floor(time_vec))
        if len(hour_selection)>1:
            list_hour=(hour>=np.min(hour_selection))*(hour<np.max(hour_selection))
        else:
            list_hour=hour>0
            
        if len(month_selection)==1:
            month_selection=np.concatenate((np.array(month_selection), np.array(month_selection)+1))
        month=np.array(time_vec-693960-2)
        month=pd.to_datetime(month, unit='D',origin=pd.Timestamp('1900-01-01')).month
        if len(month_selection)>1:
            list_month=(month>=np.min(month_selection))*(month<np.max(month_selection))
        else:
            list_month=month>0
            
        list=list_hour*list_month
        self.PSD_dist = np.percentile(input_data[list,:], percentile, axis=0)
        self.f=f
        self.percentile=percentile
        self.hour_selection=hour_selection
        self.month_selection=month_selection

    def plot_psd(self, freq_scale='linear', amplitude_range=[], f_range=[], fig_width=6, fig_height=6):
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        cmap=cm.get_cmap('jet', len(self.percentile))
        cmap_table=cmap(range(len(self.percentile)))
        
        c = np.arange(1, len(self.percentile) + 1)
        cbar = ax.scatter(c, c, c=c, cmap=cmap)
        ax.cla()
        
        for n in np.arange(len(self.percentile)):
            plt.plot(self.f, self.PSD_dist[n,:], color=cmap_table[n,:], linewidth=2)
        
        plt.xscale(freq_scale)
        if not f_range:
            plt.xlim(np.min(self.f), np.max(self.f))
        else:
            plt.xlim(np.min(f_range), np.max(f_range))
        
        if len(amplitude_range)>0:
            plt.ylim(np.min(amplitude_range), np.max(amplitude_range))
        plt.xlabel('Frequency')
        plt.ylabel('Amplitude')
        
        if len(self.percentile)>5:
            cbar=fig.colorbar(cbar, ticks=self.percentile[::int(np.ceil(len(self.percentile)/5))])
        else:
            cbar=fig.colorbar(cbar, ticks=self.percentile)
        cbar.set_label('Percentile')
        
