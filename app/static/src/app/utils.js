// Alias global functions
const globals = window.globals || {}
const cardUrl = globals.cardUrl
const parseText = globals.parseText
const initTooltips = globals.initTooltips
const initCardPopups = globals.initCardPopups
const actOnText = globals.actOnText
const assetPath = globals.assetPath
const notify = globals.notify

// Matches tutor stubs to their search requirements:
// `true` => all cards are valid targets
// `3` => cards with magic play cost equal to this
// 'Ally' => cards of type 'Ally'
const tutorCards = {
	'open-memories': true,
	'augury': 3,
	'shared-sorrow': true,
	'james-endersight': 'Ally'
}

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
	} else if (cardType === 'Conjuration' || cardType === 'Conjured Alteration Spell') {
		return 'fa-recycle'
	} else if (cardType === 'Phoenixborn') {
		return 'fa-shield'
	} else if (cardType === 'summon') {
		// Special instance; only really used by filters
		return 'fa-plus-square'
	}
	return 'fa-question-circle'
}

// Lodash `get` fails in production builds due to removing extraneous lodash methods, so...
function getFromObject (obj, path) {
	for (let i = 0, parts = path.split('.'), len = parts.length; i < len; i++) {
		obj = obj[parts[i]]
		if (obj === undefined) break
	}
	return obj
}

export {
	globals,
	cardUrl,
	parseText,
	initTooltips,
	initCardTooltips,
	teardownTooltips,
	actOnText,
	assetPath,
	typeToFontAwesome,
	getFromObject,
	notify,
	tutorCards
}
