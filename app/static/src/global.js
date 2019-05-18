// Polyfills
import 'babel-polyfill'
// Normal imports
import Noty from 'noty'
import parseText from 'base/parse_text'
import {initTextareaHelpers, actOnText} from 'base/textarea_helpers'
import {assetPath, initCardPopups, initTooltips} from 'base/tooltips'
// Import things that should execute on page load
import 'base/onload/auto_submit_forms'
import 'base/onload/static_modals'

const globals = window.globals || {}

//* Define global URL helpers and constants
globals.cardUrl = function (data) {
	return '/cards/' + data.stub + '/'
}
globals.playerUrl = function (badge) {
	return '/player/' + badge + '/'
}
globals.diceData = [
	'ceremonial', 'charm', 'illusion', 'natural',
	'divine', 'sympathy'
]
globals.releaseData = {
	'core': [0],
	'expansions': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
	'promos': [101, 102, 103]
}

//* Setup standard text parsing
globals.parseText = parseText

//* Setup tooltip handling
globals.assetPath = assetPath
globals.initCardPopups = initCardPopups
globals.initTooltips = initTooltips

//* Setup textarea helpers handling
globals.actOnText = actOnText

//* Setup global alert handling
globals.notify = function (message, category) {
	new Noty({
		type: category || 'info',
		text: message,
		timeout: category !== 'error' ? 5000 : 30000,
		theme: 'metroui'
	}).show()
}

//* Init popups for statically-rendered content
const preExistingCards = Array.from(document.querySelectorAll('.card'))
if (preExistingCards && preExistingCards.length) {
	initCardPopups(preExistingCards)
}

//* Display Flask alerts
const alerts = document.getElementById('server-alerts')
if (alerts) {
	for (const alert of Array.from(alerts.children)) {
		if (!alert.tagName || alert.tagName.toLowerCase() !== 'li') continue
		globals.notify(alert.innerHTML, alert.className)
	}
}

//* Init in-page textarea helpers
const textareaHelpers = document.querySelectorAll('.textarea-helpers')
if (textareaHelpers) {
	initTextareaHelpers(Array.from(textareaHelpers))
}
