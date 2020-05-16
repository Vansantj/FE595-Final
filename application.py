from flask import Flask, request, render_template
import pandas as pd
import numpy as np
import tensorflow as tf
import re
import os

from NeuralNet import generatePrediction


app = Flask(__name__)

@app.route('/')
def form():
	return render_template('home.html')

@app.route('/', methods=['POST'])
def form_post():
	size = request.form['size']
	start_text = request.form['start']
	output_text = generatePrediction(size, start_text)

	return output_text

if __name__ == "__main__":
	app.run()