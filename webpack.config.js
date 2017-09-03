var path = require('path')
var LodashModuleReplacementPlugin = require('lodash-webpack-plugin')
var webpack = require('webpack')
var debug = process.env.NODE_ENV !== 'production'

module.exports = {
	entry: {
		app: './app/static/src/app.js'
	},
	output: {
		filename: '[name]' + (!debug ? '.min' : '')  + '.js',
		path: path.resolve(__dirname, 'app/static/js')
	},
	module: {
		rules: [
			{
				test: /\.vue$/,
				loader: 'vue-loader'
			},
			{
				test: /\.js$/,
				loader: 'babel-loader',
				include: [path.resolve(__dirname, 'app/static/src')]
			}
		]
	},
	plugins: debug ? [] : [
		new LodashModuleReplacementPlugin,
		new webpack.optimize.UglifyJsPlugin
	]
}
