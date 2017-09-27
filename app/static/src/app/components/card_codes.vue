<template>
	<span v-html="parsedContent"></span>
</template>

<script>
	import {initCardPopups, parseCardCodes} from 'app/utils'

	export default {
		props: ['content'],
		mounted: function () {
			const els = Array.from(this.$el.querySelectorAll('.card'))
			if (els && els.length) {
				initCardPopups(els)
			}
		},
		computed: {
			parsedContent () {
				return parseCardCodes(this.content)
			}
		}
	}
</script>

