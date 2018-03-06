// Polyfills
import 'babel-polyfill'
// Normal imports
import Noty from 'noty'
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
globals.releaseData = {
	'core': [0],
	'expansions': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
	'promos': [101, 102, 103]
}
globals.parseCardCodes = function (input) {
	input = escape(input)
	// Parse card codes
	input = input.replace(/\[\[((?:[a-z -]|&#39;)+)(?::([a-z]+))?\]\]|( - )/ig, (_, primary, secondary, dash) => {
		if (dash) {
			return ' <span class="divider"></span> '
		}
		const lowerPrimary = primary.toLowerCase().replace('&#39;', '')
		secondary = secondary && secondary.toLowerCase()
		if (['discard', 'exhaust'].indexOf(lowerPrimary) > -1) {
			return ['<span class="phg-', lowerPrimary, '" title="', primary, '"></span>'].join('')
		}

		if (globals.diceData.indexOf(lowerPrimary) > -1) {
			if (!secondary) {
				secondary = 'power'
			}
		} else if (lowerPrimary === 'basic') {
			secondary = 'magic'
		} else if (lowerPrimary === 'main') {
			secondary = 'action'
		} else if (lowerPrimary === 'side') {
			secondary = 'action'
		} else if (secondary) {
			return ['<i>', lowerPrimary, ' ', secondary, '</i>'].join('')
		} else {
			var data = {stub: lowerPrimary.replace(/ /g, '-')}
			return ['<a href="', globals.cardUrl(data), '" class="card" target="_blank">', primary, '</a>'].join('')
		}
		return [
			'<span class="phg-', lowerPrimary, '-', secondary, '" title="',
			primary, (secondary ? ' ' + secondary : ''), '"></span>'
		].join('')
	})
	// Parse star formatting
	// lone star: *
	input = input.replace(/(^| )\*( |$)/g, (_, leading, trailing) => {
		return [leading, '&#42;', trailing].join('')
	})
	// ***emstrong*** or ***em*strong**
	input = input.replace(/\*{3}(.+?)\*(.*?)\*{2}/g, (_, first, second) => {
		return ['<b><i>', first, '</i>', second, '</b>'].join('')
	})
	// ***strong**em*
	input = input.replace(/\*{3}(.+?)\*{2}(.*?)\*/g, (_, first, second) => {
		return ['<i><b>', first, '</b>', second, '</i>'].join('')
	})
	// **strong**
	input = input.replace(/\*{2}(.+?)\*{2}/g, (_, text) => {
		return ['<b>', text, '</b>'].join('')
	})
	// *emphasis*
	input = input.replace(/\*([^\*\n\r]+)\*/g, (_, text) => {
		return ['<i>', text, '</i>'].join('')
	})
	return input
}

globals.assetPath = function (url) {
	if (url.charAt(0) !== '/') {
		url = '/' + url
	}
	return globals.cdnUrl + url
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

globals.initCardPopups = function (els) {
	// Setup card hover tooltips
	const tip = tippy(els, {
		delay: 250,
		position: 'left',
		html: '#card-detail-popup',
		onShow () {
			// `this` inside callbacks refers to the popper element
			const reference = tip.getReferenceElement(this)
			const imgUrl = reference.href.replace(/^(?:.*?)(\/cards\/.+?)\/?$/i, (_, url) => {
				return globals.assetPath('/images' + url + '.png')
			})
			const content = this.querySelector('.card-holder')
			content.innerHTML = '<img src="' + imgUrl + '" alt="' + reference.textContent + '" />'
		},
		onShown () {
			const reference = tip.getReferenceElement(this)
			reference.setAttribute('data-tooltip-active', '1')
		},
		onHidden () {
			const reference = tip.getReferenceElement(this)
			reference.removeAttribute('data-tooltip-active')
		}
	})
	// Setup card link click events
	for (const el of els) {
		el.addEventListener('click', function (event) {
			if (!this.getAttribute('data-tooltip-active')) {
				event.preventDefault()
				event.stopPropagation()
				// Simulate a click event on the document to auto-close all other tooltips
				document.dispatchEvent(new MouseEvent('click'))
				// And show the current tooltip
				tip.show(tip.getPopperElement(this))
			}
		})
	}
	return tip
}
// Init popups for statically-rendered content
const preExistingCards = Array.from(document.querySelectorAll('.card'))
if (preExistingCards && preExistingCards.length) {
	globals.initCardPopups(preExistingCards)
}

globals.notify = function(message, category) {
	new Noty({
		type: category || 'info',
		text: message,
		timeout: category !== 'error' ? 5000 : 30000,
		theme: 'metroui'
	}).show()
}
// Display Flask alerts
const alerts = document.getElementById('server-alerts')
if (alerts) {
	for (const alert of Array.from(alerts.children)) {
		if (!alert.tagName || alert.tagName.toLowerCase() !== 'li') continue
		globals.notify(alert.innerHTML, alert.className)
	}
}

// Setup inline modals
const triggers = document.querySelectorAll('.inline-modal-trigger')
if (triggers) {
	// Setup modal container element
	const container = document.createElement('div')
	container.className = 'modal-container'
	// Setup outer mask element
	const mask = document.createElement('div')
	mask.className = 'modal-mask modal-enter'
	mask.style.display = 'none'
	const transitionEnd = ('WebkitTransition' in document.documentElement.style) ? 'webkitTransitionEnd' : 'transitionend'
	mask.addEventListener(transitionEnd, function (event) {
		// Adjust element styling after "leave" transition
		if (this.className.indexOf(' modal-enter-to') > -1) {
			return
		}
		this.className = 'modal-mask modal-enter'
		this.style.display = 'none'
	})
	mask.addEventListener('click', function (event) {
		if (this === event.target) {
			this.className = 'modal-mask modal-leave-to'
		}
	})
	mask.appendChild(container)
	document.body.appendChild(mask)
	for (const trigger of Array.from(triggers)) {
		trigger.addEventListener('click', function (event) {
			event.preventDefault()
			// Clone our modal contents
			const contents = document.getElementById(this.hash.substr(1)).cloneNode(true)
			contents.style.display = 'block'
			// Empty our container
			while (container.lastChild) {
				container.removeChild(container.lastChild)
			}
			// Insert modal contents into the container
			container.appendChild(contents)
			mask.style.display = ''
			// We have to delay the class setting until next tick;
			// otherwise the modal-enter class will not take effect
			setTimeout(() => {
				mask.className = 'modal-mask modal-enter-to'
			}, 1)
		})
	}
}

// Setup "almost AJAX" auto-submitting form behavior
function isActiveInput (input) {
	if (input.type === 'checkbox' || input.type === 'radio') {
		return input.checked
	}
	return input.name && input.value
}
globals.formToQueryString = function (formEl) {
	const submittables = formEl.querySelectorAll('input, select, textarea')
	if (!submittables) return ''
	// Stash values into an object
	let values = {}
	for (const input of Array.from(submittables)) {
		const name = input.name
		if (isActiveInput(input)) {
			if (values[name]) {
				if (!Array.isArray(values[name])) {
					values[name] = [values[name]]
				}
				values[name].push(input.value)
			} else {
				values[name] = input.value
			}
		}
	}
	// Convert object into a query string
	return Object.keys(values).map(key => {
		const divider = encodeURIComponent(key) + '='
		if (Array.isArray(values[key])) {
			return divider + values[key].join('&' + divider)
		}
		return divider + encodeURIComponent(values[key])
	}).join("&")
}
const autoSubmitForms = document.querySelectorAll('form.auto-submit')
if (autoSubmitForms) {
	for (const form of Array.from(autoSubmitForms)) {
		function submitForm (event) {
			event.preventDefault()
			let query = globals.formToQueryString(form)
			if (!query) {
				window.location.href = window.location.origin + window.location.pathname
				return
			}
			window.location.search = '?' + query
		}
		// Submit on enter (otherwise clear buttons can hijack the enter key)
		form.addEventListener('keydown', function (event) {
			if (event.keyCode == 13) {
				submitForm(event)
			}
		})
		form.addEventListener('submit', submitForm)
		form.addEventListener('change', submitForm)
		// Setup logic for "clear" buttons
		const clearButtons = form.querySelectorAll('.clear-control')
		if (clearButtons) {
			for (const button of Array.from(clearButtons)) {
				button.addEventListener('click', function (event) {
					document.getElementById(button.getAttribute('data-target-input')).value = ''
					submitForm(event)
				})
			}
		}
	}
}
