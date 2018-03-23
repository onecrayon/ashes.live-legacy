<template>
	<span v-html="parsedContent"></span>
</template>

<script>
	import {initCardTooltips, teardownTooltips, parseText} from 'app/utils'

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
				return parseText(this.content)
			}
		}
	}
</script>
