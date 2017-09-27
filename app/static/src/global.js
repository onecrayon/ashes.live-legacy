import tippy from 'tippy.js'

var globals = window.globals || {}

globals.cardUrl = function (data) {
	return '/cards/' + data.stub
}
globals.diceData = [
	'ceremonial', 'charm', 'illusion', 'natural',
	'divine', 'sympathy'
]
globals.parseCardCodes = function (input) {
	return input.replace(/\[\[([a-z -]+)(?::([a-z]+))?\]\]|( - )/ig, function (_, primary, secondary, dash) {
		if (dash) {
			return ' <span class="divider"></span> '
		}
		const lowerPrimary = primary.toLowerCase()
		secondary = secondary && secondary.toLowerCase()
		if (['discard', 'exhaust'].indexOf(lowerPrimary) > -1) {
			return ['<span class="phg-', lowerPrimary, '" title="', primary, '"></span>'].join('')
		}
		
		if (globals.diceData.indexOf(lowerPrimary) > -1) {
			if (!secondary) {
				secondary = 'power'
			}
		} else if (lowerPrimary == 'basic') {
			secondary = 'magic'
		} else if (lowerPrimary == 'main') {
			secondary = 'action'
		} else if (lowerPrimary == 'side') {
			secondary = 'action'
		} else if (secondary) {
			return ['<i>', lowerPrimary, (secondary ? ' ' + secondary : ''), '</i>'].join('')
		} else {
			var data = {stub: lowerPrimary.replace(' ', '-')}
			return ['<a href="', globals.cardUrl(data), '" class="card">', primary, '</a>'].join('')
		}
		return [
			'<span class="phg-', lowerPrimary, '-', secondary, '" title="',
			primary, (secondary ? ' ' + secondary : ''), '"></span>'
		].join('')
	})
}

globals.initCardPopups = function (target) {
	// Setup card hover tooltips
	const tip = tippy(target, {
		theme: 'transparent',
		html: '#card-detail-popup',
		onShow: function () {
			console.log('loading?')
			// `this` inside callbacks refers to the popper element
			const reference = tip.getReferenceElement(this)
			const imgUrl = reference.href.replace(/(\/cards\/.+)$/i, '/images$1.png')
			const content = this.querySelector('.tippy-tooltip-content')
			content.innerHTML = '<img src="' + imgUrl + '" alt="' + reference.textContent + '" />'
		}
	})
}
// Init popups for statically-rendered content
globals.initCardPopups('.card')
