import tippy from 'tippy.js'
import {escape} from 'lodash'

var globals = window.globals || {}

globals.cardUrl = function (data) {
	return '/cards/' + data.stub
}
globals.diceData = [
	'ceremonial', 'charm', 'illusion', 'natural',
	'divine', 'sympathy'
]
globals.parseCardCodes = function (input) {
	return input.replace(/\[\[([a-z' -]+)(?::([a-z]+))?\]\]|( - )/ig, function (_, primary, secondary, dash) {
		if (dash) {
			return ' <span class="divider"></span> '
		}
		const lowerPrimary = primary.toLowerCase().replace('\'', '')
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
			return ['<i>', escape(lowerPrimary), (secondary ? ' ' + escape(secondary) : ''), '</i>'].join('')
		} else {
			var data = {stub: escape(lowerPrimary.replace(/ /g, '-'))}
			return ['<a href="', globals.cardUrl(data), '" class="card" target="_blank">', escape(primary), '</a>'].join('')
		}
		return [
			'<span class="phg-', escape(lowerPrimary), '-', escape(secondary), '" title="',
			escape(primary), (secondary ? ' ' + escape(secondary) : ''), '"></span>'
		].join('')
	})
}

globals.initTooltips = function (el) {
	const els = (el && [el]) || Array.from(this.$el.querySelectorAll('.tooltip'))
	if (els && els.length) {
		const tip = tippy(els, {
			delay: 250,
			position: 'bottom-start',
			interactive: true,
			interactiveBorder: 10,
			multiple: true,
			onShow: function () {
				const content = this.querySelector('.tippy-tooltip-content')
				if (!/(?:^| )parsed-card-content/.test(content.className)) {
					content.innerHTML = globals.parseCardCodes(content.textContent)
					content.className = content.className + ' parsed-card-content'
					const moreEls = content.querySelectorAll('.card')
					if (moreEls) {
						globals.initCardPopups(Array.from(moreEls))
					}
				}
			}
		})
		this.tip = tip
	}
}

globals.initCardPopups = function (target) {
	// Setup card hover tooltips
	const tip = tippy(target, {
		delay: 250,
		html: '#card-detail-popup',
		onShow: function () {
			// `this` inside callbacks refers to the popper element
			const reference = tip.getReferenceElement(this)
			const imgUrl = reference.href.replace(/(\/cards\/.+?)\/?$/i, '/images$1.png')
			const content = this.querySelector('.card-holder')
			content.innerHTML = '<img src="' + imgUrl + '" alt="' + reference.textContent + '" />'
		}
	})
	return tip
}
// Init popups for statically-rendered content
globals.initCardPopups('.card')
