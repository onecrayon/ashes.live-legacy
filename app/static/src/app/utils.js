import tippy from 'tippy.js'

// Alias global functions
const cardUrl = globals.cardUrl
const parseCardCodes = globals.parseCardCodes
const initCardPopups = globals.initCardPopups

function initCardTooltips (el) {
	const els = (el && [el]) || Array.from(this.$el.querySelectorAll('.card'))
	if (els && els.length) {
		this.tip = initCardPopups(els)
	}
}

function initTooltips (el) {
	const els = (el && [el]) || Array.from(this.$el.querySelectorAll('.tooltip'))
	if (els && els.length) {
		const tip = tippy(els, {
			delay: 250,
			position: 'bottom-start',
			onShow: function () {
				const content = this.querySelector('.tippy-tooltip-content')
				if (!/(?:^| )parsed-card-content/.test(content.className)) {
					content.innerHTML = parseCardCodes(content.textContent)
					content.className = content.className + ' parsed-card-content'
				}
			}
		})
		this.tip = tip
	}
}

function teardownTooltips () {
	if (this.tip) {
		this.tip.destroyAll()
		this.tip = null
	}
}

export {
	cardUrl,
	parseCardCodes,
	initTooltips,
	initCardTooltips,
	teardownTooltips
}
