var path = require('path')
var LodashModuleReplacementPlugin = require('lodash-webpack-plugin')
var webpack = require('webpack')
var debug = process.env.NODE_ENV !== 'production'

module.exports = {
	entry: {
		'app': path.resolve(__dirname, './app/static/src/app.js'),
		'global' : path.resolve(__dirname, './app/static/src/global.js')
	},
	output: {
		path: path.resolve(__dirname, 'app/static/js'),
		filename: '[name]' + (!debug ? '.min' : '')  + '.js'
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
	resolve: {
		alias: {
			'app': path.resolve(__dirname, 'app/static/src/app'),
			'base': path.resolve(__dirname, 'app/static/src/base')
		}
	},
	plugins: debug ? [] : [
		new webpack.DefinePlugin({
			'process.env': {
				NODE_ENV: '"production"'
			}
		}),
		new LodashModuleReplacementPlugin
	]
}
