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
