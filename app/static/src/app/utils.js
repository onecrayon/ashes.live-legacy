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

function initTooltips (targets) {
	return tippy(targets, {
		delay: 250
	})
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
