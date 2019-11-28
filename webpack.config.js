var path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var jquery = require('jquery')
var chartjs = require('chart.js')

module.exports = {
  mode:'development',
  entry:  path.join(__dirname, 'assets/src/js/index'), 
  output: {
      path: path.join(__dirname, 'assets/dist'),
      filename: '[name]-[hash].js'
    },
  plugins: [
      new BundleTracker({
        path: __dirname,
        filename: 'webpack-stats.json'
      }),
    ],
}
