var path = require('path')

module.exports = {
	entry: {
		app: './app/static/src/app.js'
	},
	output: {
		filename: '[name].js',
		path: path.resolve(__dirname, 'app/static/js')
	},
	module: {
		rules: [
			{
				test: /\.vue$/,
				loader: 'vue-loader'
			}
		]
	}
}
