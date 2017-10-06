// Alias global functions
const globals = window.globals || {}
const cardUrl = globals.cardUrl
const parseCardCodes = globals.parseCardCodes
const initTooltips = globals.initTooltips
const initCardPopups = globals.initCardPopups
const assetPath = globals.assetPath

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

function typeToFontAwesome (cardType) {
	if (cardType === 'Ally') {
		return 'fa-users'
	} else if (cardType === 'Action Spell') {
		return 'fa-asterisk'
	} else if (cardType === 'Reaction Spell') {
		return 'fa-bolt'
	} else if (cardType === 'Alteration Spell') {
		return 'fa-clone'
	} else if (cardType === 'Ready Spell') {
		return 'fa-share-square'
	} else if (cardType === 'summon') {
		// Special instance; only really used by filters
		return 'fa-plus-square'
	}
	return 'fa-question-circle'
}

export {
	globals,
	cardUrl,
	parseCardCodes,
	initTooltips,
	initCardTooltips,
	teardownTooltips,
	assetPath,
	typeToFontAwesome
}
