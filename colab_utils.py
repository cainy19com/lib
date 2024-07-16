"""
this file has to be self contained
"""


import tensorflow as tf
import keras as K

import numpy as np
import math

import matplotlib.pyplot as plt
import PIL

import os
import sys
import shutil
import time

import glob
import hashlib

import requests
from concurrent.futures import ThreadPoolExecutor


def DISPLAY(x):
  x = tf.convert_to_tensor(x)
  if x.ndim == 5:
    x = tf.concat([v for v in x], 1)
  if x.ndim == 4:
    x = tf.concat([v for v in x], 1)
  display(K.utils.array_to_img(x))


def PLT_LOSS_12(loss, title, figsize=(10, 5)):
  """
  inp: a list of loss
  """

  if len(loss) == 0:
    print("loss list is empty")
    return

  l = len(loss)

  cur = loss[-1]
  min = np.min(loss)
  max = np.max(loss)
  min5 = np.sort(loss)[:5]
  min5_i = np.argsort(loss)[:5]

  plt.rcParams["figure.figsize"] = figsize
  fig, axes = plt.subplots(1, 2)

  axes[0].plot(range(1, l + 1), loss)

  axes[0].plot(min5_i + 1, min5, "g*")

  for i in range(len(min5)):
    xy = (min5_i[i] + 1, min5[i])
    xytext = ((l + 1) / 2, max - (max - min) / 10 * i)
    axes[0].annotate(
      round(min5[i], 4),
      xy=xy, 
      xytext=xytext, 
      arrowprops={"arrowstyle": "->", "color": "black", "alpha": 0.1},
      ha="center",
      va="center",
      alpha=0.5,
    )
    0 and axes[0].text(
        min5_i[i] + 1, 
        min5[i], 
        round(min5[i], 4),
        horizontalalignment="center", 
        verticalalignment="top",
        rotation=15, 
        wrap=True
    )

  axes[1].plot(np.sort(range(l, 0, -1))[-50:], loss[-50:])

  fig.suptitle(title)
  plt.show()


def TIME(start):
  """
  inp: time in sec
  """
  now = time.time()
  diff = now - start
  hour = diff // 3600
  min = (diff % 3600) // 60
  sec = int(diff % 60)
  return "{}h {}m {}s".format(hour, min, sec)


def load_ds(dir,
            img_h, 
            img_w,
            batch_size,
            labels="inferred", 
            crop_to_aspect_ratio=False,
            pre=None,
            aug=None):
  """
  pre: must be a seq model, pre process 
  aug: must be a seq model, aug men tation
  when there is no sub dir, labels must be set to none
  """
  ds = K.utils.image_dataset_from_directory(
    dir,
    image_size=(img_h, img_w),
    labels=labels,
    crop_to_aspect_ratio=crop_to_aspect_ratio,
    shuffle=False, # in pipe line
    batch_size=None, # in pipe line
  )

  AUTOTUNE = tf.data.AUTOTUNE

  if pre:
    ds = ds.map(lambda x: pre(x), num_parallel_calls=AUTOTUNE)
  if aug:
    ds = ds.map(lambda x: aug(x, training=True), num_parallel_calls=AUTOTUNE)
  ds = ds.shuffle(tf.data.experimental.cardinality(ds))
  ds = ds.batch(batch_size)
  ds = ds.prefetch(AUTOTUNE)

  return ds


def offset_cosine_schedule(t, T, max=0.95, min=0.02):
  """
  inp: (None, 1, 1, 1)
  ret: ((None, 1, 1, 1), (None, 1, 1, 1))
  """

  rad_min = tf.acos(max)
  rad_max = tf.acos(min)

  rad = rad_min + tf.cast(t / T, "float32") * (rad_max - rad_min)

  sig_ratio = tf.cos(rad)
  noi_ratio = tf.sin(rad)

  return sig_ratio, noi_ratio


def sinusoidal_embedding(t, length=32):
  """
  inp: (None, 1, 1, 1)
  ret: (None, 1, 1, length)
  t used here to em injec of time or seq
  length must be even
  """
  half = length / 2
  f = 1000 ** (tf.range(half) / (half - 1))
  sin = tf.sin(2 * math.pi * f * t)
  cos = tf.cos(2 * math.pi * f * t)
  return tf.concat([sin, cos], axis=3)


class CBTime(K.callbacks.Callback):
  def __init__(self, freq):
    self.freq = freq
    self.epoch_in_sec = []
    self.train_start = time.time()

  def on_epoch_begin(self, epoch, logs=None):
    self.epoch_start = time.time()

  def on_epoch_end(self, epoch, logs=None):
    self.epoch_in_sec.append(time.time() - self.epoch_start)

    print("total:", TIME(self.train_start))
    print("cur epoch:", TIME(self.epoch_start))

    if epoch > 0:
      print("avg time per epoch:", np.mean(self.epoch_in_sec))
      print("avg time per epoch after 1st:", np.mean(self.epoch_in_sec[1:]))
      print("min epoch time:", np.min(self.epoch_in_sec))
      print("max epoch time:", np.max(self.epoch_in_sec))

    if epoch > 0 and (epoch + 1) % self.freq == 0:
      self.plot()

  def on_train_end(self, logs=None):
    self.plot()

  def plot(self):
    min = [t / 60 for t in self.epoch_in_sec]
    plt.plot(range(1, len(min) + 1), min)
    plt.title("time per epoch (min)")
    plt.show()


class CBStop(K.callbacks.Callback):
  def __init__(self):
    f = open("/content/stop", "w")
    f.write("no")
    f.close()

  def check(self):
    if open("/content/stop").read().strip() == "yes":
      self.model.stop_training = True

  def on_train_batch_begin(self, batch, logs=None):
    self.check()

  def on_train_batch_end(self, batch, logs=None):
    self.check()

  def on_epoch_begin(self, epoch, logs=None):
    self.check()

  def on_epoch_end(self, epoch, logs=None):
    self.check()


def con_cur_dl(urls, workers=30):
  """
  inp: set, list
  out: xxx dir
  """

  os.mkdir("xxx")

  urls = list(set(urls))
  urls = [url.strip() for url in urls]
  urls = [url for url in urls if url]

  print("total unique urls:", len(urls))

  dled = []

  def dl(index, url):
    r = requests.get(url, allow_redirects=True)
    f = open(f"xxx/{index + 1}", "wb")
    f.write(r.content)
    f.close()
    dled.append(index) # list append thread safe
    if len(dled) % workers == 0:
      print("file dl ed so far:", len(dled))

  pool = None
  for index, url in enumerate(urls):
    if not pool:
      pool = ThreadPoolExecutor(max_workers=workers)

    pool.submit(dl, index, url)

    if (index + 1) % workers != 0:
      continue

    pool.shutdown(wait=True)
    pool = None

  time.sleep(10) # wait for the last batch
  print("file dl ed:", len(os.listdir("xxx")))


def mv_num_file(num, src, dst):
  fs = os.listdir(src)
  fs.sort()
  for f in fs[:num]:
    os.rename(f"{src}/{f}", f"{dst}/{f}")


def find_dups(dir):
  """
  inp: abs path
  """
  os.chdir(dir)
  os.mkdir("dup")

  files = glob.glob(f"{dir}/**", recursive=True)
  files = [f for f in files if os.path.isfile(f)]
  print("num of files:", len(files))

  unique = []
  names = []
  for i, file in enumerate(files):
    rb = open(file, "rb").read()
    hash = hashlib.sha256(rb).hexdigest()
    if hash not in unique:
      unique.append(hash)
      names.append(file)
    else:
      dup_of_name = names[unique.index(hash)].split("/")[-1]
      os.rename(file, "dup/{}-{}".format(dup_of_name, i))
  
  print("num of dups found:", len(files) - len(unique))


def make_favicon(img_path):
  """
  Make favicon, apple touch icon in curr dir
  """
  img = PIL.Image.open(img_path)

  img.resize((200, 200)).save("favicon.ico")
  img.resize((200, 200)).save("apple-touch-icon.png")

