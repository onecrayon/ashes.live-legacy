import {escape} from 'lodash'

/**
 * Parses the given input and converts card codes and star formatting into HTML.
 * 
 * @param {string} input 
 */
export default function parseText (input) {
	input = escape(input)
	// Parse links
	input = input.replace(
		/\[\[([^\]]*?)((?:https?:\/\/|\b)[^\s\/$.?#]+\.[^\s*]+?)\]\]|(https?:\/\/[^\s\/$.?#]+\.[^\s*]+?(?=[.?)][^a-z]|!|\s|$))/ig,
		(_, text, url, standalone) => {
			let internalLink = false
			const textUrl = url ? url : standalone
			const parsedUrl = textUrl.replace(/^(https?:\/\/)?(.+)$/i, (_, prefix, url) => {
				if (/^ashes\.live(?:\/.*)?$/i.test(url)) {
					internalLink = true
					return 'https://' + url
				} else if (!prefix) {
					return 'http://' + url
				} else {
					return url
				}
			})
			text = text ? text.trim() : null
			return [
				'<a href="', parsedUrl, '"', !internalLink ? ' rel="nofollow"' : '', '>',
				text ? text : textUrl, '</a>'
			].join('')
		}
	)
	// Parse player links
	input = input.replace(/\[\[([^\]]*?)#([0-9](?:[a-z0-9*&+=-]|&amp;)+[a-z0-9*!])\]\]/ig, (_, text, badge) => {
		text = text ? text.trim() : null
		return [
			'<a class="username" href="', globals.playerUrl(badge), '">',
			text ? text : '', '<span class="badge">#', badge, '</span></a>'
		].join('')
	})
	// Parse card codes
	input = input.replace(/\[\[((?:[a-z -]|&#39;)+)(?::([a-z]+))?\]\]|( - )/ig, (input, primary, secondary, dash) => {
		if (dash) {
			return ' <span class="divider"><span class="alt-text">-</span></span> '
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
			primary, (secondary ? ' ' + secondary : ''), '"><span class="alt-text">', input,
			'</span></span>'
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
