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
		var lowerPrimary = primary.toLowerCase()
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
