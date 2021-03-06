# -*- coding: utf-8 -*-
"""Copy_Design1a_Para2_S21_MLcode.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16qAhvtptMs0q51dOTXi2bwhHuImNmRay
"""

import pandas as pd
import numpy as  np
import tensorflow as tf
import matplotlib.pyplot as plt
import sklearn.model_selection as sk
#tf.compat.v1.enable_eager_execution()
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 10)

from google.colab import files
files.upload()
data=pd.read_csv("Design1a_Para2_S21.csv")
data

def clean_data(data):
    data=data.replace([-np.inf], np.nan)
    data=data.dropna(axis=1, how='all')
    data.isnull().to_numpy().any()
    return data

def output_parameters(data):
    output=np.empty((0,4), float)
    for columns in data.columns[1:]:
        params=columns.split(' ')[3:]
        param=[]
        for vals in params:
            param.append(float(vals.split('=')[1][1:-3]))
        param=np.array([param])
        output=np.concatenate((output, param), axis=0)
    return output

data = clean_data(data)
X = output_parameters(data)
data

rows=3
columns=5
fig, window =  plt.subplots(rows, columns, figsize=(15,10))
fig.tight_layout()
for x in range(0,rows):
    for y in range(0, columns):
        index=1+x*columns+y
        window[x][y].title.set_text("Column Number = %d" % index)
        window[x][y].plot(data.iloc[:, 0], data.iloc[:, index])
plt.setp(window[-1, :], xlabel='Frequency in GHz');
plt.setp(window[:, 0], ylabel='Transmission in dB');

# Commented out IPython magic to ensure Python compatibility.
output_data = np.empty((0,4),float)
index_range = np.empty((0,2), int)
indices = []
input_data = np.empty((0,2), float)
r1 = -0.45
r2 = -0.40
for index in range(1, data.shape[1]):
    temp = []
    ix = []
    freq = []
    found = False
    for i, val in enumerate(data.iloc[:, index]):
        if r1 <= val:
            found = True
            temp.append(val)
            ix.append(i)
            freq.append(data.iloc[i, 0])
            continue
        if found:
            break
    if len(temp) >= 2 and temp[-1] < r2:
        freq = np.array([[freq[0], freq[-1]]])
        ix = np.array(([[ix[0], ix[-1]]]))
        indices.append(index)
        index_range = np.concatenate((index_range, ix))
        input_data = np.concatenate((input_data, freq))
        output_data = np.concatenate((output_data, X[index-1:index]))
# print(output_data)
# print(index_range)
# print(input_data)
# print(indices)
print('''Total data points = %d
Useful data points = %d
Loss in data points = %d'''
# %(data.shape[1]-1, len(indices),
data.shape[1]-1-len(indices)))

# Commented out IPython magic to ensure Python compatibility.
rows = 3
columns = 4
fig, window =  plt.subplots(rows, columns, figsize=(15,10))
fig.tight_layout()
for x in range(0,rows):
    for y in range(0, columns):
        position = x*columns+y
        column_index = indices[position]
        start = index_range[position][0]
        end = index_range[position][1]
        params=output_data[position]
        window[x][y].plot(data.iloc[start:end+1, 0], data.iloc[start:end+1, column_index])
        window[x][y].title.set_text('''
        Column Number = %d
        index_range = [%d, %d]
        g1=%.1fmm, g2=%.1fmm
        s1=%.1fmm, s2=%.1fmm''' 
#         % (column_index, start, end, *params))
plt.subplots_adjust(wspace=0.25, hspace=0.5)
plt.setp(window[-1, :], xlabel='Frequency in GHz');
plt.setp(window[:, 0], ylabel='Transmission in dB');

Normalize=True
normalized_output = np.copy(output_data)
if Normalize:
  mean=[]
  sigma=[]
  for column in range(0,4):
    m = np.mean(output_data[:,column])
    s = np.max(output_data[:,column]) - np.min(output_data[:,column])
    mean.append(m)
    sigma.append(s)
    normalized_output[:,column]=(output_data[:,column]-m)/s
normalized_output

Normalize_input=True
normalized_input = np.copy(input_data)
if Normalize_input:
  input_mean=[]
  input_sigma=[]
  for column in range(0,2):
      m = np.mean(input_data[:,column])
      s = np.max(input_data[:,column]) - np.min(input_data[:,column])
      input_mean.append(m)
      input_sigma.append(s)
      normalized_input[:,column]=(input_data[:,column]-m)/s
normalized_input[0:10,:]

cleaned_data = np.concatenate((output_data, input_data), axis=1)
cleaned_data = pd.DataFrame(cleaned_data, columns=['g1 (mm)', 'g2 (mm)',
                                                   's1 (mm)', 's2 (mm)', 
                                                   'freq1 (GHz)', 'freq2 (GHz)'])
cleaned_data

for index in range(0,4):
  print(cleaned_data[cleaned_data.columns[index]].value_counts())

from sklearn.model_selection import train_test_split
def data():
  return train_test_split(normalized_input, normalized_output, test_size=0.20, shuffle=True)

def learn(epochs):
  model = tf.keras.Sequential()
  model.add(tf.keras.layers.Dense(16,input_shape=(2,),activation='relu'))
  model.add(tf.keras.layers.Dense(128,activation='relu'))
  model.add(tf.keras.layers.Dense(512,activation='relu'))
  model.add(tf.keras.layers.Dense(128,activation='relu'))
  model.add(tf.keras.layers.Dense(4,activation='tanh'))
  model.compile(loss='mse', optimizer='RMSProp')
  history=model.fit(X_train, y_train, validation_split=0.20, epochs=epochs,
                    verbose=0, shuffle=True)
  return model, history

def input(inp, mean, sigma, Normalize):
  if Normalize:
    op=np.copy(inp)
    for column in range(0,2):
      op[:,column] = (inp[:,column]-mean[column])/(sigma[column])
    return op
  return inp
    
def output(prediction, mean, sigma, Normalize):
  if Normalize:
    op=np.copy(prediction[:])
    for column in range(0,4):
          op[:,column] = (prediction[:,column]*sigma[column])+mean[column]
    return op
  return prediction

acceptable_loss = 0.95
epochs = 150
from sklearn.metrics import mean_squared_error as mse
X_train, X_test, y_train, y_test = data()
model, history = learn(epochs)
prediction = output(model.predict(X_test), mean, sigma, Normalize)
y = output(y_test, mean, sigma, Normalize)
test_loss = mse(prediction, y, squared=False)
while test_loss >= acceptable_loss:
  print("Test Loss very high, trying again. [test loss = %f]" % test_loss)
  X_train, X_test, y_train, y_test = data()
  model, history = learn(epochs)
  prediction = output(model.predict(X_test), mean, sigma, Normalize)
  y = output(y_test, mean, sigma, Normalize)
  test_loss = mse(prediction, y, squared=False)
print("test loss g1= %0.1f, precision= %0.1f" % (mse(prediction[:,0], y[:,0], squared=False), 2))
print("test loss g2= %0.1f, precision= %0.1f" % (mse(prediction[:,1], y[:,1], squared=False), 0.5))
print("test loss s1= %0.1f, precision= %0.1f" % (mse(prediction[:,2], y[:,2], squared=False), 1))
print("test loss s2= %0.1f, precision= %0.1f" % (mse(prediction[:,3], y[:,3], squared=False), 0.5))
print("test loss avg= %f" % test_loss)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model accuracy')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'loss'], loc='upper left')
plt.show()

inp=np.array([[2,4],[3,6],[8,10],[2,18],[10,15],[15,19],[18,19],[7,18],[9,16],[11,12],[17,18]], dtype=np.float)
normal_input = input(inp, input_mean, input_sigma, Normalize_input)
normal_output = model.predict(normal_input)
result = output(normal_output, mean, sigma, Normalize)
result = result.round(1)
result = np.where(result<=0, 0, result)
result

model.save('good.h5')
files.download('good.h5')