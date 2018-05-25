<template>
	<span class="ashes-500-points">
		<span class="active">{{ card.data.ashes_500_costs[0].qty_1 }}</span
		><span v-if="card.data.ashes_500_costs[0].qty_2 !== null">
			\ <span :class="{active: card.count >= 2}">{{ card.data.ashes_500_costs[0].qty_2 }}</span
		></span
		><span v-if="card.data.ashes_500_costs[0].qty_3 !== null">
			\ <span :class="{active: card.count >= 3}">{{ card.data.ashes_500_costs[0].qty_3 }}</span
		></span>
		<span v-if="card.data.ashes_500_costs.length > 1 || card.data.ashes_500_combos">
			<!-- TODO: add title and tooltip logic to show the combo details on tap/hover -->
			<!-- TODO: add active class if any combo is added to the score -->
			<i class="fa fa-exclamation-circle"></i>
		</span>
	</span>
</template>

<script>
	import {initCardTooltips, teardownTooltips} from 'app/utils'

	export default {
		props: ['card'],
		mounted: function () {
			initCardTooltips.call(this, this.$el)
		},
		updated: function () {
			teardownTooltips.call(this)
			initCardTooltips.call(this, this.$el)
		},
		beforeDestroy: teardownTooltips
	}
</script>
