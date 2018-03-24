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
				let valuePrefix = value.slice(0, start)
				const valueSelection = value.slice(start, end)
				let valueSuffix = value.slice(end)

				// Make sure we have strings for prefix/suffix so length property works
				if (!prefix) prefix = ''
				if (!suffix) suffix = ''

				// No selection? Default to the end of the value
				if (!start && !end && start !== 0) {
					end = value.length
					start = end
				}

				if (prefix || suffix) {
					start += prefix.length
					end += prefix.length
				} else if (linePrefix) {
					// TODO: process line prefixes
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
