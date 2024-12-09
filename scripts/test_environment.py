import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask
from transformers import pipeline
import torch
print("PyTorch available:", torch.cuda.is_available())  # Should print False on Raspberry Pi

#import tensorflow as tf
#print("TensorFlow version:", tf.__version__)
print("Environment is set up successfully!")
