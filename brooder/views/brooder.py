# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, session, redirect, url_for, \
    request, flash, g, jsonify, abort
from Brooder.brooder import Brooder
from Brooder.config import Config
from Brooder.temp import Sensor

mod = Blueprint('brooder', __name__)

@mod.route('/')
def index():
  """
    Get the list of active sensors
  """
  sensor_list = Brooder().listAll()
  config = Config()
  config._sensor = Sensor(id=config.reference)
  for sensor in sensor_list:
    sensor.current_value = round(sensor._sensor.value, 1)
    if sensor.set_temperature:
      sensor.max_value = round(sensor.set_temperature, 1)
    else:
      if sensor.cycle_enabled:
        sensor.max_value = round(config.rampedTemp(sensor.cycle_started),1)
      else:
        sensor.max_value = round(config.temp_high, 1)

  return render_template('brooder/index.html', sensor_list = sensor_list, config = config)

@mod.route('/config/', methods=['GET', 'POST'])
def config():
  """
    Set up configuration
  """
  config = Config()
  changed = False
  if request.method == "POST":
    for key in request.form:
      if config.setValueFromForm(key, request.form[key]):
        changed = True
    if changed:
      flash('Config saved')
      config.save()

  return render_template('brooder/config.html', config=config)

@mod.route('/node/<nid>/', methods=['GET', 'POST'])
def node(nid):
  """
    Get or set stats on a single sensor
  """
  node = Brooder()
  node.load(int(nid)) # This avoids calling the pin init.
  node._sensor = Sensor(id=node.sensor)
  config = Config()

  node.current_value = round(node._sensor.value,1)
  if node.set_temperature:
    node.max_value = round(node.set_temperature,1)
  elif node.cycle_enabled:
    node.max_value = round(config.rampedTemp(node.cycle_started),1)
  else:
    node.max_value = round(config.temp_high, 1)

  if request.method == "POST":
    # Find what we've been given and update the config
    if ('power' in request.form and request.form['power']):
      node.setEnabled(request.form['power'] == 'on')
    if ('cycle' in request.form and request.form['cycle']):
      node.setCycle(request.form['cycle'] == 'on')
    elif ( 'set' in request.form ):
      node.setTemperature(request.form['temp'])
    elif ( 'default' in request.form and request.form['default'] == '1' ):
      node.setDefault()
    elif ('refresh' in request.form):
      pass
    node.load(node.id)

  return render_template('brooder/node.html', node = node, config=config)
