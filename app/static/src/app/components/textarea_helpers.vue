<template>
	<div class="textarea-helpers responsive-cols">
		<div class="btn-group col">
			<button class="btn btn-small" type="button" title="Bold" @mousedown="boldText"
				><i class="fa fa-bold"></i></button
			><button class="btn btn-small" type="button" title="Italic" @mousedown="italicText"
				><i class="fa fa-italic"></i></button>
		</div>
		<div class="btn-group col">
			<button class="btn btn-small" type="button" title="List" @mousedown="listText"
				><i class="fa fa-list-ul"></i></button
			><button class="btn btn-small" type="button" title="Quote" @mousedown="quoteText"
				><i class="fa fa-quote-left"></i></button>
		</div>
		<div class="btn-group col-flex">
			<button class="btn btn-small" type="button" title="Wrap with [[ ]]"
				@mousedown="cardCodeText"><strong>[[&hellip;]]</strong></button>
		</div>
	</div>
</template>

<script>
export default {
	methods: {
		boldText (event) {
			event.preventDefault()
			this.$emit('actOnText', {prefix: '**', suffix: '**'})
		},
		italicText (event) {
			event.preventDefault()
			this.$emit('actOnText', {prefix: '*', suffix: '*'})
		},
		listText (event) {
			event.preventDefault()
			this.$emit('actOnText', {linePrefix: '* '})
		},
		quoteText (event) {
			event.preventDefault()
			this.$emit('actOnText', {linePrefix: '> '})
		},
		cardCodeText (event) {
			event.preventDefault()
			this.$emit('actOnText', {prefix: '[[', suffix: ']]'})
		}
	}
}
</script>

