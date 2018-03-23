function isActiveInput (input) {
	if (input.type === 'checkbox' || input.type === 'radio') {
		return input.checked
	}
	return input.name && input.value
}

export function formToQueryString (formEl) {
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
	}).join('&')
}
