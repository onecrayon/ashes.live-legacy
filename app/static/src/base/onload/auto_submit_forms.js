import {formToQueryString} from 'base/forms'

// Setup "almost AJAX" auto-submitting form behavior
function submitForm (event) {
	event.preventDefault()
	let query = formToQueryString(this)
	const baseUrl = (
		window.location.origin + window.location.pathname.replace(/\/\d+\/?$/, '')
	)
	if (!query) {
		window.location.href = baseUrl
	} else {
		window.location.href = [baseUrl, '?', query].join('')
	}
}

const autoSubmitForms = document.querySelectorAll('form.auto-submit')
if (autoSubmitForms) {
	for (const form of Array.from(autoSubmitForms)) {
		form.addEventListener('submit', submitForm.bind(form))
		form.addEventListener('change', submitForm.bind(form))
	}
}
