var path = require('path')

module.exports = {
	entry: {
		deckbuilder: './app/static/src/app.js'
	},
	output: {
		filename: 'app.js',
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