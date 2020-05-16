# -*- coding: utf-8 -*-
"""
Created on Fri May 15 19:10:22 2020

@author: jvan1
"""

import pandas as pd
import numpy as np
import tensorflow as tf
import re
import os
character_dict = dict()
batch_size = 128
def getTextBatch(text_list):
    ind = np.random.randint(0,len(text_list))
    text = text_list[ind]
    text = re.sub(r'[^a-zA-Z0-9 ]','',str(text).replace('-',' '))
    if len(text)>13:
        snippet_ind = np.random.randint(0,max(len(text)-11,1))
        snippet = text[snippet_ind:snippet_ind+11]
        return snippet
    else:
        return getTextBatch(text_list)
def setUpText():
    data = pd.read_csv('Tweets.csv')
    text_list = list(data['Tweets'].values)
    return text_list

def textToInt(snippet,character_dict):
    need_to_add = list(set([x for x in snippet if x not in list(character_dict.keys())]))
    current_ind = len(character_dict.values())
    for i in range(0,len(need_to_add)):
        character_dict[need_to_add[i]] = current_ind
        current_ind = current_ind+1
    return [character_dict[x] for x in snippet]


def buildModel(batch_size):
  rnn_units = 256
  vocab_size = len(character_dict.values())
  model = tf.keras.Sequential([    
    tf.keras.layers.Embedding(vocab_size+1, 256,
                              batch_input_shape=[batch_size, None]),
    tf.keras.layers.GRU(rnn_units,
                        return_sequences=True,
                        stateful=True,
                        recurrent_initializer='glorot_uniform'),
    tf.keras.layers.Dense(vocab_size+1)
  ])
  return model
def loss(labels, logits):
  return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)
def trainModel(batch_size,model,text_list,save_callback,character_dict):
    to_pass_x = []
    to_pass_y = []
    for i in range(0,batch_size):
    
        snip = getTextBatch(text_list)
        total = textToInt(snip,character_dict)
        to_pass_x.append(total[:-1])
        to_pass_y.append(total[1:])

    
    x = np.array(to_pass_x)
    y = np.array(to_pass_y)
    model.fit(x=x,y=y,callbacks=[save_callback],epochs=1)
    return model
def addToDict(character_dict):
    text_list = setUpText()
    text_list = [re.sub(r'[^a-zA-Z0-9 ]','',str(x).replace('-',' ')) for x in text_list]
    text_list = [str(x) for x in text_list]
    all_char = ''.join([str(x) for x in set(''.join(text_list))])
    all_char = re.sub(r'[^a-zA-Z0-9 ]','',all_char.replace('-',' '))
    textToInt(all_char,character_dict)
    return character_dict
def runModel(character_dict):

    epochs = 10000
    character_dict = addToDict(character_dict)
    text_list = setUpText()
    model = buildModel(batch_size)
    save_folder = './NN_Saves'
    try:
        model.load_weights(tf.train.latest_checkpoint(save_folder))
        print('Weights loaded')
    except:
        print('Weights not loaded')
        pass
    model.compile(optimizer='adam', loss=loss)
    

    save = os.path.join(save_folder, "NN_Save_{loss:.2f}")

    save_callback=tf.keras.callbacks.ModelCheckpoint(
            filepath=save,
            save_weights_only=True)

    for i in range(epochs):
        trainModel(batch_size,model,text_list,save_callback,character_dict)

def generatePrediction(size,start_text):
    character_dict = addToDict(dict())
    model = buildModel(1)
    save_folder = './NN_Saves'
    model.load_weights(tf.train.latest_checkpoint(save_folder))

    model.build(tf.TensorShape([1, None]))
    pred_text = []
    for i in range(size):
        x = textToInt(start_text[-10:],character_dict)
        predictions = model.predict(np.array([x]))
        predicted_id = tf.random.categorical(predictions[0], num_samples=1)[-1,0]
        with tf.compat.v1.Session() as sess:  predicted_id = predicted_id.eval()
        char = list(character_dict.keys())[predicted_id]
        pred_text.append(char)
        start_text = start_text+char
    return start_text+''.join(pred_text)

if __name__=='__main__':
    runModel(character_dict)