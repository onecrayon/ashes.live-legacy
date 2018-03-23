import tippy from 'tippy.js'
import parseText from 'base/parse_text'

export function assetPath (url) {
	if (url.charAt(0) !== '/') {
		url = '/' + url
	}
	return window.globals.cdnUrl + url
}

export function initCardPopups (els) {
	// Setup card hover tooltips
	const tip = tippy(els, {
		delay: 250,
		position: 'left',
		html: '#card-detail-popup',
		onShow () {
			// `this` inside callbacks refers to the popper element
			const reference = tip.getReferenceElement(this)
			const imgUrl = reference.href.replace(/^(?:.*?)(\/cards\/.+?)\/?$/i, (_, url) => {
				return assetPath('/images' + url + '.png')
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

export function initTooltips (el) {
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
					content.innerHTML = parseText(content.textContent)
					content.className = content.className + ' parsed-card-content'
					const moreEls = content.querySelectorAll('.card')
					if (moreEls) {
						initCardPopups(Array.from(moreEls))
					}
				}
			}
		})
		this.tip = tip
	}
}
