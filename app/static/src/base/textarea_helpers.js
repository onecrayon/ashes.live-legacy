/**
 * Act on textarea text based on button input
 * 
 * @param {string} text The text to modify
 * @param {int} start The selection starting index
 * @param {int} end The selection ending index
 * @param {object} actions An object with `prefix`, `suffix`, and/or `linePrefix` keys
 */
export function actOnText (text, start, end, actions) {
	const prefix = actions.prefix || ''
	const suffix = actions.suffix || ''
	const linePrefix = actions.linePrefix || ''
	let textPrefix, textSelection, textSuffix

	// No selection? Default to the end of the value
	if (!start && !end && start !== 0) {
		end = text.length
		start = end
	}

	if (prefix || suffix) {
		textPrefix = text.slice(0, start)
		textSelection = text.slice(start, end)
		textSuffix = text.slice(end)
		start += prefix.length
		end += prefix.length
	} else if (linePrefix) {
		let lineRangeStart = start
		let lineRangeEnd = end
		const maxRange = text.length
		while (lineRangeStart > 0 && text.charAt(lineRangeStart - 1) !== '\n') {
			lineRangeStart--
		}
		if (text.charAt(lineRangeEnd) !== '\n') {
			while (lineRangeEnd < maxRange && text.charAt(lineRangeEnd + 1) !== '\n') {
				lineRangeEnd++
			}
		}
		const lines = text.slice(lineRangeStart, lineRangeEnd).split('\n')
		textPrefix = text.slice(0, lineRangeStart)
		textSuffix = text.slice(lineRangeEnd)
		textSelection = linePrefix + lines.join('\n' + linePrefix)
		start = end = lineRangeEnd + (lines.length * linePrefix.length)
	} else {
		// Don't both proceeding if we don't actually have anything to parse
		return
	}

	text = [
		textPrefix,
		prefix,
		textSelection,
		suffix,
		textSuffix
	].join('')

	return {text, start, end}
}

export function initTextareaHelpers (els) {
	for (const parentDiv of els) {
		const textarea = parentDiv.nextElementSibling
		if (!textarea) continue
		const buttons = parentDiv.querySelectorAll('button')
		for (const button of Array.from(buttons)) {
			button.addEventListener('mousedown', (event) => {
				event.preventDefault()
				const actions = {
					prefix: button.getAttribute('data-cursor-prefix'),
					suffix: button.getAttribute('data-cursor-suffix'),
					linePrefix: button.getAttribute('data-line-prefix')
				}
				const logic = actOnText(
					textarea.value, textarea.selectionStart, textarea.selectionEnd, actions
				)
				if (!logic) return
				textarea.value = logic.text
				textarea.focus()
				textarea.setSelectionRange(logic.start, logic.end)
			})
		}
	}
}
