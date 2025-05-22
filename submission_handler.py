
from supabase import create_client
import os
import tensorflow as tf
from transformers import TFAutoModel, AutoTokenizer
import numpy as np

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

