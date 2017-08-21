const express = require('express');
const app = express();
const mdns = require('mdns');
const fs = require('fs');
const multer = require('multer');

let storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, __dirname + '/uploads/')
    },
    filename: function (req, file, cb) {
        cb(null, 'emoji.jpg')
  }
})
let upload = multer({
  storage: storage
});

let config = require('./config.json');

let ad = mdns.createAdvertisement(mdns.tcp('http'), 3000, {name: 'NYCTS'});
ad.start();

const jsonReplacer = (key, value) => {
  if(value === 'false') return false
  if(value === 'true') return true
  return value
}


const writeToConfigFile = (callback) => {
  fs.writeFile('./config.json', JSON.stringify(config, jsonReplacer, '  '), (err) => {
    if(err) console.log(err);
    callback();
  });
}

app.get('/', function (req, res) {
  res.json(config)
});

app.get('/getConfig', function (req, res) {
  res.json(config)
});

app.get('/setConfig/:route/:settingKey/:settingValue', function (req, res) {
  config[req.params.route][req.params.settingKey] = req.params.settingValue;
  writeToConfigFile(() => res.json(config));
});

app.get('/getLogo', function (req, res) {
  console.log(config.logo.image_file);
  res.sendFile(config.logo.image_file, {root: __dirname + '/uploads/'});
});

app.post('/setLogo', upload.single('image'), function (req, res) {
  console.log(req.body);
  res.json(req.body);
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!')
});
