const textareaHelpers = document.querySelectorAll('.textarea-helpers')
if (textareaHelpers) {
	for (const parentDiv of Array.from(textareaHelpers)) {
		const textarea = parentDiv.nextElementSibling
		if (!textarea) continue
		const buttons = parentDiv.querySelectorAll('button')
		for (const button of Array.from(buttons)) {
			button.addEventListener('mousedown', (event) => {
				event.preventDefault()
				let prefix = button.getAttribute('data-cursor-prefix')
				let suffix = button.getAttribute('data-cursor-suffix')
				const linePrefix = button.getAttribute('data-line-prefix')
				let start = textarea.selectionStart
				let end = textarea.selectionEnd
				const value = textarea.value
				let valuePrefix, valueSelection, valueSuffix

				// Make sure we have strings for prefix/suffix so length property works
				if (!prefix) prefix = ''
				if (!suffix) suffix = ''

				// No selection? Default to the end of the value
				if (!start && !end && start !== 0) {
					end = value.length
					start = end
				}

				if (prefix || suffix) {
					valuePrefix = value.slice(0, start)
					valueSelection = value.slice(start, end)
					valueSuffix = value.slice(end)
					start += prefix.length
					end += prefix.length
				} else if (linePrefix) {
					let lineRangeStart = start
					let lineRangeEnd = end
					const maxRange = value.length
					while (lineRangeStart > 0 && value.charAt(lineRangeStart - 1) !== '\n') {
						lineRangeStart--
					}
					if (value.charAt(lineRangeEnd) !== '\n') {
						while (lineRangeEnd < maxRange && value.charAt(lineRangeEnd + 1) !== '\n') {
							lineRangeEnd++
						}
					}
					const lines = value.slice(lineRangeStart, lineRangeEnd).split('\n')
					valuePrefix = value.slice(0, lineRangeStart)
					valueSuffix = value.slice(lineRangeEnd)
					valueSelection = linePrefix + lines.join('\n' + linePrefix)
					start = end = lineRangeEnd + (lines.length * linePrefix.length)
				} else {
					// Don't both proceeding if we don't actually have anything to parse
					return
				}

				// FIXME: find a way to modify textarea value without destroying undo/redo queue
				textarea.value = [
					valuePrefix,
					prefix,
					valueSelection,
					suffix,
					valueSuffix
				].join('')
				textarea.focus()
				textarea.setSelectionRange(start, end)
			})
		}
		// TODO: Add automatic parsing of the enter/return keys to add new list elements and terminate open inline tags
	}
}
