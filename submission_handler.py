
from supabase import create_client
import os
import tensorflow as tf
from transformers import TFAutoModel, AutoTokenizer
import numpy as np

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

new_submissions = supabase.table("submissions").select("*").execute()
new_submissions = new_submissions.data

tokenizer = AutoTokenizer.from_pretrained("allenai/specter")
encoder = TFAutoModel.from_pretrained("allenai/specter")

def calc_pref_vec(text):
  entries = text.strip().split("\n>")
  papers = []

  for entry in entries:
    lines = entry.strip().split("\n", 1)
    title = lines[0].lstrip(">")
    abstract = lines[1]
    papers.append(f"{title} {tokenizer.sep_token} {abstract}")

  inputs = tokenizer(papers, padding=True, return_tensors="tf")
  results = encoder(**inputs)
  last = results.last_hidden_state[:, 0, :]
  embeds = tf.nn.l2_normalize(last, axis=1) # this is the raw EagerTensor output
  embeds = tf.keras.backend.get_value(embeds)

  avg_embed = np.mean(embeds, axis=0)
  pref_vec = avg_embed / np.linalg.norm(avg_embed)

  return(pref_vec)

for i in range(0,len(new_submissions)):
  existing_user = supabase.table("users").select("id").eq("email", new_submissions[i]["email"]).execute()
  exists = bool(existing_user.data)
  if exists:
    no_abstract_update = new_submissions[i]["abstracts"] == None
    if no_abstract_update: # for an existing user who's not updating their preference vec
      data = {
        "email": new_submissions[i]["email"],
        "journals": new_submissions[i]["journals"],
        "frequency": new_submissions[i]["frequency"],
        "digest_length": new_submissions[i]["digest_length"]
      }
      response = supabase.table("users").update(data).eq("email", new_submissions[i]["email"]).execute()
      if response.data:
        supabase.table("submissions").delete().eq("email", new_submissions[i]["email"]).execute()
  else:
    pref_vec = calc_pref_vec(new_submissions[i]["abstracts"])
    data = {
    "email": new_submissions[i]["email"],
    "journals": new_submissions[i]["journals"],
    "frequency": new_submissions[i]["frequency"],
    "digest_length": new_submissions[i]["digest_length"],
    "embedding" : pref_vec.tolist() # tolist is important to make sure the data sent is JSON serialisable
    }
    response = supabase.table("users").insert(data).execute()
    if response.data:
      supabase.table("submissions").delete().eq("email", new_submissions[i]["email"]).execute()