<template>
	<span v-html="parsedContent"></span>
</template>

<script>
	import {initCardTooltips, teardownTooltips, parseCardCodes} from 'app/utils'

	export default {
		props: ['content'],
		mounted: initCardTooltips,
		updated: function () {
			teardownTooltips.call(this)
			initCardTooltips.call(this)
		},
		beforeDestroy: teardownTooltips,
		computed: {
			parsedContent () {
				return parseCardCodes(this.content)
			}
		}
	}
</script>
