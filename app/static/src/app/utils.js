// Alias global functions
const cardUrl = globals.cardUrl
const parseCardCodes = globals.parseCardCodes
const initTooltips = globals.initTooltips
const initCardPopups = globals.initCardPopups

function initCardTooltips (el) {
	const els = (el && [el]) || Array.from(this.$el.querySelectorAll('.card'))
	if (els && els.length) {
		this.tip = initCardPopups(els)
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